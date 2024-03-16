<template>
  <a-card title="Available Tasks">
    <a-collapse v-model:activeKey="activeKey">
      <template v-for="(item, uuid) in projectListStore.projectListState.projects" :key="uuid">
        <template v-if="Object.keys(taskListStore.activeTaskListState.projects[uuid] ?? {}).length">
          <a-collapse-panel
            :key="uuid"
            :header="`${item.name}: ${Object.keys(taskListStore.activeTaskListState.projects[uuid]).length}`"
          >
            <table>
              <tr>
                <th>Task</th>
                <th>Detail</th>
              </tr>
              <template
                v-for="(task_item, task_uuid) in taskListStore.activeTaskListState.projects[uuid]"
                :key="task_uuid"
              >
                <tr>
                  <td>{{ task_item.name }}</td>
                  <td>{{ task_item.detail }}</td>
                </tr>
              </template>
            </table>
          </a-collapse-panel>
        </template>
      </template>
    </a-collapse>
  </a-card>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useProjectListStore, useTaskListStore } from '@/store/projects'

const projectListStore = useProjectListStore()
const taskListStore = useTaskListStore()

const activeKey = ref(['1'])
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
