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
        v-model:selectedKeys="helpMenuSelectedKeys"
        v-model:openKeys="helpMenuOpenKeys"
        mode="inline"
        :style="{ height: '100%', borderRight: 0 }"
      >
        <a-menu-item key="help-control">
          <ToolOutlined />
          <span>
            <router-link to="tutorial">Tutorial</router-link>
          </span>
        </a-menu-item>
        <a-menu-item key="help-authentication">
          <UnlockOutlined />
          <span>
            <router-link to="authentication">Authentication</router-link>
          </span>
        </a-menu-item>
        <a-menu-item key="help-connection">
          <LinkOutlined />
          <span>
            <router-link to="connection">Connection</router-link>
          </span>
        </a-menu-item>
        <a-menu-item key="help-manual">
          <StopOutlined />
          <span>
            <router-link to="manual">Manual</router-link>
          </span>
        </a-menu-item>
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

<script lang="ts" setup>
import { ref } from "vue";
import {
  ToolOutlined,
  UnlockOutlined,
  BuildOutlined,
  LinkOutlined,
  StopOutlined,
} from "@ant-design/icons-vue";

const collapsed = ref<boolean>(false);
const helpMenuSelectedKeys = ref<string[]>(["help-control"]);
const helpMenuOpenKeys = ref<string[]>(["help-control"]);
</script>
