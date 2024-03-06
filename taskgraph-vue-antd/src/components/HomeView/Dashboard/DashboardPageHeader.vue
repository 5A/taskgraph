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
        Sync Status
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
import { computed, toRaw } from 'vue'
import { storeToRefs } from 'pinia'
import {
  WarningTwoTone,
  CheckCircleTwoTone,
  CloseCircleTwoTone,
  SyncOutlined
} from '@ant-design/icons-vue'
import { useConnectionStatusStore, RestfulStatus, WebSocketStatus } from '@/store/connection'
import { useProjectListStore } from '@/store/projects'
import { type ProjectListItem } from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'

const connStatusStore = useConnectionStatusStore()
const { connStatusState } = storeToRefs(connStatusStore)

const projectListStore = useProjectListStore()

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
}

</script>

<style scoped>
.dashboard-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
</style>
