<template>
    <BgShare title="图像" :uploadPath="currentUser.userAvatars" />
</template>

<script>
import BgShare from './ImageUpload.vue'
import { useCurrentUserStore } from "@/stores/user";

export default {
    props: {},
    components: {
        BgShare
    },
    data() {
        return {
        };
    },
    setup() {
        const currentUser = useCurrentUserStore();
        return { currentUser };
    },
    watch: {},
    computed: {},
    mounted() { },
    methods: {},
};
</script>