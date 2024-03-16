<template>
  <a-card title="Projects Overview">
    <template #extra>
      <a-button type="primary" @click="showNewProjectModal"> <PlusCircleOutlined />New </a-button>
    </template>
    <a-modal
      v-model:open="newProjectModalOpen"
      title="Create New Project"
      @ok="handleNewProjectModalOk"
    >
      <a-input
        v-model:value="projectOperationInputStore.newProjectInputState.name"
        placeholder="Project Name"
      />
    </a-modal>
    <a-collapse v-model:activeKey="activeKey">
      <a-collapse-panel
        v-for="(item, uuid) in projectListStore.projectListState.projects"
        :key="uuid"
        :header="item.name"
      >
        <template #extra>
          <a-tag
            v-if="projectListStore.projectListState.projects[uuid].status == 'Active'"
            color="blue"
          >
            Active
          </a-tag>
          <a-tag
            v-else-if="projectListStore.projectListState.projects[uuid].status == 'Snoozed'"
            color="green"
          >
            Snoozed
          </a-tag>
          <a-tag v-else-if="projectListStore.projectListState.projects[uuid].status == 'Done'">
            Done
          </a-tag>
          <a-tag v-else color="red"> Unknown Status </a-tag>
        </template>
        <p>Project Name: {{ item.name }}</p>
        <p>Project ID: {{ uuid }}</p>
      </a-collapse-panel>
    </a-collapse>
  </a-card>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { message as ant_message } from 'ant-design-vue'
import { PlusCircleOutlined } from '@ant-design/icons-vue'
import { useProjectListStore, useProjectOperationInputStore } from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'

const projectListStore = useProjectListStore()
const projectOperationInputStore = useProjectOperationInputStore()

const newProjectModalOpen = ref<boolean>(false)

const showNewProjectModal = () => {
  newProjectModalOpen.value = true
}

const handleNewProjectModalOk = (_e: MouseEvent) => {
  createNewProject()
  newProjectModalOpen.value = false
}

async function createNewProject() {
  const target_value = projectOperationInputStore.newProjectInputState.name
  console.log('Creating new project: ', target_value)
  const result = await callRESTfulAPI(
    'projects',
    'POST',
    JSON.stringify({
      name: target_value
    })
  )
  if (result?.id) {
    projectListStore.projectListState.projects[result.id] = { name: result.name, status: 'Active' }
  } else {
    ant_message.warning('Error calling RESTful API, see console for more info.')
  }
}

const activeKey = ref(['1'])
</script>
