<template>
  <a-card title="Available Tasks">
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
import { PlusCircleOutlined } from '@ant-design/icons-vue'
import { useProjectListStore, useProjectOperationInputStore } from '@/store/projects'
import { type ProjectListItem } from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'
const labelCol = { style: { width: '150px' } }
const wrapperCol = { span: 14 }

const projectListStore = useProjectListStore()
const projectOperationInputStore = useProjectOperationInputStore()

const activeKey = ref(['1'])
</script>
