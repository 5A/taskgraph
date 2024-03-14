<template>
  <a-breadcrumb style="margin: 16px 0">
    <a-breadcrumb-item>TaskGraph</a-breadcrumb-item>
    <a-breadcrumb-item>Workbench</a-breadcrumb-item>
    <a-breadcrumb-item>Dashboard</a-breadcrumb-item>
  </a-breadcrumb>
  <DashboardPageHeader />
  <br />
  <a-layout-content
    :style="{
      background: '#fff',
      padding: '24px',
      margin: 0,
      minHeight: '280px',
    }"
  >
    <AvailableTasksCard />
  </a-layout-content>
</template>

<script lang="ts" setup>
import DashboardPageHeader from "./Dashboard/DashboardPageHeader.vue";
import AvailableTasksCard from "./Dashboard/AvailableTasksCard.vue";
</script>

<style scoped></style>
