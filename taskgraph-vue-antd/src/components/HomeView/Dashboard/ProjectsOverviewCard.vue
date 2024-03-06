<template>
  <a-card title="Projects Overview">
    <template #extra>
      <a-button type="primary" @click="showNewProjectModal"> New </a-button>
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
        <p>Project Name: {{ item.name }}</p>
        <p>Project ID: {{ uuid }}</p>
      </a-collapse-panel>
    </a-collapse>
  </a-card>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { message as ant_message } from 'ant-design-vue'
import { useProjectListStore, useProjectOperationInputStore } from '@/store/projects'
import { type ProjectListItem } from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'
const labelCol = { style: { width: '150px' } }
const wrapperCol = { span: 14 }

const projectListStore = useProjectListStore()
const projectOperationInputStore = useProjectOperationInputStore()

const newProjectModalOpen = ref<boolean>(false)

const showNewProjectModal = () => {
  newProjectModalOpen.value = true
}

const handleNewProjectModalOk = (e: MouseEvent) => {
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
    projectListStore.projectListState.projects[result.id] = { name: result.name }
  } else {
    ant_message.warning('Error calling RESTful API, see console for more info.')
  }
}

const activeKey = ref(['1'])
</script>
