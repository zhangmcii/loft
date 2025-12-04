<template>
    <BgShare title="背景" :uploadPath="currentUser.userBackgroundUrl" />
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