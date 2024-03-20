<template>
  <a-layout>
    <a-layout-sider
      width="220"
      style="background: #fff"
      v-model:collapsed="collapsed"
      collapsedWidth="60"
      collapsible
    >
      <a-menu
        v-model:selectedKeys="projectsMenuSelectedKeys"
        v-model:openKeys="projectsMenuOpenKeys"
        mode="inline"
        :style="{ height: '100%', borderRight: 0 }"
      >
        <a-menu-item key="projects-manage">
          <AppstoreAddOutlined />
          <span>
            <router-link to="/projects/manage">Manage</router-link>
          </span>
        </a-menu-item>
        <a-sub-menu key="projects-unfinished">
          <template #title>
            <ProjectOutlined />
            <span>Projects</span>
          </template>
          <a-menu-item
            v-for="(item, uuid) in projectListStore.projectListState.projects"
            :key="uuid"
          >
            <ExperimentOutlined />
            <span>
              <router-link :to="{ name: 'project_id', params: { project_uuid: uuid } }">
                {{ item.name }}
              </router-link>
            </span>
          </a-menu-item>
        </a-sub-menu>
      </a-menu>
    </a-layout-sider>
    <a-layout style="padding: 0 24px 24px">
      <router-view />
      <a-layout-footer style="text-align: center">
        TaskGraph Web UI ©2024 taskgraph.org
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ProjectOutlined, ExperimentOutlined, AppstoreAddOutlined } from '@ant-design/icons-vue'

import { useProjectListStore } from '@/store/projects'
const projectListStore = useProjectListStore()

const collapsed = ref<boolean>(false)
const projectsMenuSelectedKeys = ref<string[]>(['projects-manage'])
const projectsMenuOpenKeys = ref<string[]>(['projects-unfinished'])
</script>
