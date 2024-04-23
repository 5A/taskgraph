<template>
  <a-card title="Available Tasks">
    <a-collapse v-model:activeKey="activeKey">
      <template
        v-for="(item, project_uuid) in projectListStore.projectListState.projects"
        :key="project_uuid"
      >
        <template
          v-if="Object.keys(taskListStore.activeTaskListState.projects[project_uuid] ?? {}).length"
        >
          <a-collapse-panel
            :key="project_uuid"
            :header="`${item.name}: ${Object.keys(taskListStore.activeTaskListState.projects[project_uuid]).length}`"
          >
            <a-table
              :columns="available_tasks_table_columns"
              :data-source="available_tasks_data_source[project_uuid] ?? []"
              bordered
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.dataIndex === 'operation'">
                  <a-flex gap="small">
                    <a-button
                      key="1"
                      type="primary"
                      @click="onSetTaskDone(project_uuid, record.key)"
                    >
                      <template #icon>
                        <CheckCircleOutlined />
                      </template>
                      Done
                    </a-button>
                    <a-button key="2" @click="onCheckDetail(project_uuid, record.key)">
                      <template #icon>
                        <AimOutlined />
                      </template>
                      Check
                    </a-button>
                  </a-flex>
                </template>
              </template>
            </a-table>
          </a-collapse-panel>
        </template>
      </template>
    </a-collapse>
  </a-card>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { CheckCircleOutlined, AimOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { Dayjs } from 'dayjs'
import {
  useProjectListStore,
  useTaskListStore,
  useProjectOperationInputStore
} from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'

const router = useRouter()
const projectListStore = useProjectListStore()
const taskListStore = useTaskListStore()

const projectOperationInputStore = useProjectOperationInputStore()
const projectInputState = projectOperationInputStore.projectWorkspaceInputState

const activeKey = ref(['1'])

const available_tasks_table_columns = [
  {
    title: 'Task',
    dataIndex: 'task',
    key: 'task'
  },
  {
    title: 'Detail',
    dataIndex: 'detail',
    key: 'detail'
  },
  {
    title: 'Operation',
    dataIndex: 'operation',
    key: 'operation'
  }
]

const available_tasks_data_source = computed(() => {
  let transformedDataSource: Record<string, Array<object>> = {}
  for (const project_uuid in taskListStore.activeTaskListState.projects) {
    transformedDataSource[project_uuid] = []
    for (const task_uuid in taskListStore.activeTaskListState.projects[project_uuid]) {
      transformedDataSource[project_uuid].push({
        task: taskListStore.activeTaskListState.projects[project_uuid][task_uuid].name,
        detail: taskListStore.activeTaskListState.projects[project_uuid][task_uuid].detail,
        key: task_uuid
      })
    }
  }
  return transformedDataSource
})

async function syncStatus() {
  // if task status updated, call this function to retrive a list of tasks by GET
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

async function onSetTaskDone(project_uuid: string, task_uuid: string) {
  await callRESTfulAPI(
    `projects/${project_uuid}`,
    'POST',
    JSON.stringify({
      update_task_status: {
        uuid: task_uuid,
        status: 'Done'
      }
    })
  ).then((response) => {
    if (response?.result == 'OK') {
      message.info('Task marked as done')
      syncStatus()
    }
  })
}

function onCheckDetail(project_uuid: string, task_uuid: string) {
  // Navigates to user to corresponding project page
  router.push({ path: `projects/${project_uuid}` }).then(() => {
    projectInputState.selected_node = task_uuid
  })
  console.log(project_uuid, task_uuid)
}
</script>

<style scoped>
th {
  border-width: 1px;
  padding: 8px;
  border-style: solid;
  border-color: #666666;
  background-color: #dedede;
}

td {
  border-width: 1px;
  padding: 8px;
  border-style: solid;
  border-color: #666666;
  background-color: #ffffff;
}
</style>
