<template>
  <a-layout>
    <a-layout-header class="header">
      <div class="logo">
        <img
          style="height: 100%; width: 100%; object-fit: contain"
          alt="Nonadiabatic Logo"
          src="./assets/PNG/logo100px-white.png"
        />
        <div class="title-group">
          <!-- <div class="main-title">Quick Control</div> -->
          <!-- <div class="sub-main-title">Some Subtitle</div> -->
        </div>
      </div>
      <a-menu
        v-model:selectedKeys="selected_tab"
        theme="dark"
        mode="horizontal"
        :style="{ lineHeight: '64px' }"
      >
        <a-menu-item key="home_tab">
          <a-space>
            <HomeOutlined />
            <router-link to="/">TaskGraph</router-link>
          </a-space>
        </a-menu-item>
        <a-menu-item key="projects_tab">
          <a-space>
            <BarsOutlined />
            <router-link to="/projects">Projects</router-link>
          </a-space>
        </a-menu-item>
        <a-menu-item key="help_tab">
          <a-space>
            <QuestionCircleOutlined />
            <router-link to="/help">Help</router-link>
          </a-space>
        </a-menu-item>
        <a-menu-item key="about_tab">
          <a-space>
            <ExclamationCircleOutlined />
            <router-link to="/about">About</router-link>
          </a-space>
        </a-menu-item>
      </a-menu>
    </a-layout-header>
    <router-view />
  </a-layout>
</template>

<script lang="ts" setup>
import { ref } from "vue";
import {
  HomeOutlined,
  BarsOutlined,
  QuestionCircleOutlined,
  ExclamationCircleOutlined,
} from "@ant-design/icons-vue";
const selected_tab = ref<string[]>(["home_tab"]);
// watchEffect(() => {
//   console.log(selected_tab.value);
// });
</script>

<style scoped>
.logo {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  gap: 10px;
  float: left;
  width: auto;
  height: 40px;
  margin: 12px 10px;
  color: #fff;
  /* background: rgba(255, 255, 255, 0.3); */
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.main-title {
  white-space: nowrap;
  font-size: 24px;
  line-height: 24px;
  /* margin: 0px 10px; */
}

.sub-main-title {
  white-space: nowrap;
  font-size: 18px;
  line-height: 18px;
  /* margin: 0px 10px; */
}

.site-layout-background {
  background: #fff;
}
</style>
