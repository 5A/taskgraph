<template>
    <a-breadcrumb style="margin: 16px 0">
      <a-breadcrumb-item>Projects</a-breadcrumb-item>
      <a-breadcrumb-item>Project Management</a-breadcrumb-item>
    </a-breadcrumb>
    <ManagementHeader />
    <br />
    <a-layout-content
      :style="{
        background: '#fff',
        padding: '24px',
        margin: 0,
        minHeight: '280px',
      }"
    >
      <a-empty />
    </a-layout-content>
  </template>
  
  <script lang="ts" setup>
  import ManagementHeader from "./Manage/ManagementHeader.vue";
  </script>
  
  <style scoped></style>