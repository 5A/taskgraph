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
        v-model:selectedKeys="homeMenuSelectedKeys"
        v-model:openKeys="homeMenuOpenKeys"
        mode="inline"
        :style="{ height: '100%', borderRight: 0 }"
      >
        <a-sub-menu key="taskgraph-control">
          <template #title>
            <ExperimentOutlined />
            <span>Workbench</span>
          </template>
          <a-menu-item key="dashboard-item">
            <ToolOutlined />
            <span>
              <router-link to="dashboard">Dashboard</router-link>
            </span>
          </a-menu-item>
          <a-menu-item key="authentication-item">
            <UnlockOutlined />
            <span>
              <router-link to="authentication">Authentication</router-link>
            </span>
          </a-menu-item>
          <a-menu-item key="connection-item">
            <LinkOutlined />
            <span>
              <router-link to="connection">Connection</router-link>
            </span>
          </a-menu-item>
          <a-menu-item key="messages-item">
            <BugOutlined />
            <span>
              <router-link to="messages">Messages</router-link>
            </span>
          </a-menu-item>
        </a-sub-menu>
        <a-sub-menu key="advanced-settings">
          <template #title>
            <CodeOutlined />
            <span>Advanced</span>
          </template>
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
import {
  ToolOutlined,
  UnlockOutlined,
  ExperimentOutlined,
  LinkOutlined,
  CodeOutlined,
  BugOutlined,
  StopOutlined
} from '@ant-design/icons-vue'

import { useProjectListStore, useProjectOperationInputStore } from '@/store/projects'
const projectListStore = useProjectListStore()


const collapsed = ref<boolean>(false)
const homeMenuSelectedKeys = ref<string[]>(['dashboard-item'])
const homeMenuOpenKeys = ref<string[]>(['taskgraph-control'])
</script>
