<template>
  <a-page-header
    class="management-header"
    style="border: 1px solid rgb(235, 237, 240)"
    title="Project Management"
    sub-title="Add, Delete or Change"
  >
    <template #extra>
      <a-button key="1" type="primary">
        <SyncOutlined />
        Sync
      </a-button>
    </template>
    <a-descriptions size="small" :column="{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }">
      <a-descriptions-item label="Total Projects"> Placeholder </a-descriptions-item>
    </a-descriptions>
  </a-page-header>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import {
  WarningTwoTone,
  CheckCircleTwoTone,
  CloseCircleTwoTone,
  DeleteOutlined,
  SyncOutlined
} from '@ant-design/icons-vue'
import { useProjectListStore, useTaskGraphDataStore } from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'
</script>

<style scoped>
.project-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
</style>
