<template>
  <a-page-header
    class="dashboard-page-header"
    style="border: 1px solid rgb(235, 237, 240)"
    title="Dashboard"
    sub-title="Overview"
  >
    <template #extra>
      <a-button key="1" type="primary" @click="onSyncStatus">
        <SyncOutlined />
        Sync
      </a-button>
    </template>
    <a-descriptions size="small" :column="{ xxl: 4, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }">
      <a-descriptions-item label="Total Projects">
        {{ projectListStore.number_of_projects }}
      </a-descriptions-item>
    </a-descriptions>
  </a-page-header>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue'
import { SyncOutlined } from '@ant-design/icons-vue'
import { useProjectListStore, useTaskListStore } from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'

const projectListStore = useProjectListStore()
const taskListStore = useTaskListStore()

onMounted(() => {
  // When user loads this page, automatically refresh the project list
  onSyncStatus()
})

async function onSyncStatus() {
  // retrive a list of projects by GET
  await callRESTfulAPI('projects', 'GET', null).then((response) => {
    if (response?.projects) {
      // purge and reconstruct local buffer
      projectListStore.projectListState.projects = {}
      for (const item in response.projects) {
        projectListStore.projectListState.projects[item] = response.projects[item]
      }
    }
  })
  // retrive a list of tasks by GET
  await callRESTfulAPI('tasks/Active', 'GET').then((response) => {
    if (response?.result) {
      // purge and reconstruct local buffer
      taskListStore.activeTaskListState.projects = {}
      for (const item in response.result) {
        taskListStore.activeTaskListState.projects[item] = response.result[item]
      }
    }
  })
}
</script>

<style scoped>
.dashboard-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
</style>
