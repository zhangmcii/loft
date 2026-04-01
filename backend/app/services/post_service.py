import logging

from ..application.dto import ActionResult, ItemResult, PageResult
from ..domain.common.constants import PermissionCode
from ..domain.common.exceptions import NotFoundError
from ..domain.common.unit_of_work import UnitOfWork
from ..domain.ports.assemblers import ResponseAssemblerPort
from ..domain.ports.notifications import NotificationDispatcherPort
from ..domain.post.policies import (
    build_post_image_entities,
    build_post_summary,
    build_post_summary_image_refs,
    ensure_can_edit_post,
    normalize_post_type,
    validate_post_content,
)
from .hot_posts_service import HotPostsService


class PostService:
    def __init__(
        self,
        *,
        uow: UnitOfWork,
        assembler: ResponseAssemblerPort,
        notifier: NotificationDispatcherPort,
        hot_posts: HotPostsService,
    ):
        self.uow = uow
        self.assembler = assembler
        self.notifier = notifier
        self.hot_posts = hot_posts

    @staticmethod
    def can_publish(*, user) -> bool:
        return bool(user and user.can(PermissionCode.WRITE))

    def list_posts(
        self, *, page: int, per_page: int, viewer=None, tab_name: str | None = None
    ):
        if tab_name == "hot":
            return self.hot_posts.list_hot_posts(
                page=page, per_page=per_page, viewer=viewer
            )
        page_entities = self.uow.posts.list_posts(
            page=page,
            per_page=per_page,
            viewer=viewer,
            tab_name=tab_name,
        )
        posts = page_entities.items
        if not posts:
            return PageResult(data=[], total=page_entities.total)

        extra_data_map = self.uow.posts.build_post_extra_data_map(
            posts,
            viewer_id=(viewer.id if viewer else None),
        )
        return PageResult(
            data=self.assembler.batch_map_posts(
                posts,
                extra_data_map=extra_data_map,
                is_list=True,
            ),
            total=page_entities.total,
        )

    def search_posts(self, *, keyword: str, page: int, per_page: int, viewer=None):
        normalized_keyword = keyword.strip()
        if not normalized_keyword:
            return PageResult(data=[], total=0)

        page_entities = self.uow.posts.search_posts(
            keyword=normalized_keyword,
            page=page,
            per_page=per_page,
            viewer=viewer,
        )
        posts = page_entities.items
        if not posts:
            return PageResult(data=[], total=page_entities.total)

        extra_data_map = self.uow.posts.build_post_extra_data_map(
            posts,
            viewer_id=(viewer.id if viewer else None),
        )
        return PageResult(
            data=self.assembler.batch_map_posts(
                posts,
                extra_data_map=extra_data_map,
                is_list=True,
            ),
            total=page_entities.total,
        )

    def get_post(self, post_id: int, *, viewer=None):
        post = self.uow.posts.get_post_detail(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        extra_data_map = self.uow.posts.build_post_extra_data_map(
            [post], viewer_id=(viewer.id if viewer else None)
        )
        return ItemResult(
            data=self.assembler.batch_map_posts(
                [post],
                extra_data_map=extra_data_map,
                is_list=False,
            )[0]
        )

    def create_post(
        self, *, author, content: str, post_type: str = "text", images=None
    ):
        images = images or []
        validate_post_content(content)

        try:
            mapped_type = normalize_post_type(post_type)
            summary_preview = build_post_summary(
                content,
                post_type=post_type,
                image_refs=build_post_summary_image_refs(images=images),
            )
            post = self.uow.posts.create_post(
                author=author,
                content=content,
                summary=summary_preview.summary,
                has_more=summary_preview.is_truncated,
                post_type_value=mapped_type.value,
                has_image=bool(images),
            )
            self.uow.posts.add(post)
            self.uow.flush()

            image_payloads = build_post_image_entities(post_id=post.id, images=images)
            image_entities = self.uow.posts.create_post_images(image_payloads)
            self.uow.posts.add_images(image_entities)
            self.uow.commit()

            self._dispatch_new_post_notification(
                post_id=post.id, author_id=author.id, repo=self.uow.posts
            )
            logging.info("创建新文章: user_id=%s, post_id=%s", author.id, post.id)
            return ActionResult(message="发布文章成功", data={"post_id": post.id})
        except Exception:
            self.uow.rollback()
            raise

    def delete_post(self, *, post_id: int):
        post = self.uow.posts.get_active_post(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        logging.info("逻辑删除文章: id=%s", post.id)
        post.deleted = True
        self.uow.commit()
        try:
            self.hot_posts.remove_post(post_id=post.id)
        except Exception:
            logging.warning("热门榜移除文章失败(忽略): id=%s", post.id, exc_info=True)
        return ActionResult(message="文章删除成功")

    def edit_post(self, *, post_id: int, operator, payload: dict):
        post = self.uow.posts.get_post_for_update(post_id)
        if not post:
            raise NotFoundError("文章不存在")

        ensure_can_edit_post(operator, post)

        content = payload.get("content")
        images = payload.get("images")

        if content:
            post.content = content
        if images:
            image_payloads = build_post_image_entities(post_id=post.id, images=images)
            image_entities = self.uow.posts.create_post_images(image_payloads)
            self.uow.posts.add_images(image_entities)

        if content or images:
            summary_image_refs = (
                build_post_summary_image_refs(images=images)
                if images
                else self._load_summary_image_refs(post)
            )
            summary_preview = build_post_summary(
                post.content,
                post_type=post.derived_type,
                image_refs=summary_image_refs,
            )
            post.summary = summary_preview.summary
            post.has_more = summary_preview.is_truncated

        self.uow.commit()
        extra_data_map = self.uow.posts.build_post_extra_data_map(
            [post], viewer_id=operator.id
        )
        return ItemResult(
            data=self.assembler.batch_map_posts(
                [post],
                extra_data_map=extra_data_map,
                is_list=False,
            )[0]
        )

    def _dispatch_new_post_notification(self, *, post_id: int, author_id: int, repo):
        follower_ids = repo.list_follower_ids(author_id=author_id)
        self.notifier.dispatch_new_post(
            post_id=post_id, author_id=author_id, follower_ids=follower_ids
        )

    def _load_summary_image_refs(self, post):
        extra_data_map = self.uow.posts.build_post_extra_data_map([post])
        images = extra_data_map.get(post.id, {}).get("images", [])
        return build_post_summary_image_refs(images=images)
