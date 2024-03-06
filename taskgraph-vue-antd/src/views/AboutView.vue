<template>
  <a-layout style="padding: 0 24px 24px">
    <a-layout-content
      :style="{
        background: '#fff',
        padding: '24px',
        margin: '16px 0',
        minHeight: '280px'
      }"
    >
      <a-typography>
        <a-typography-title :level="1">About</a-typography-title>
        <a-typography-paragraph>
          This application is part of the TaskGraph project. Visit
          <a-typography-link href="https://taskgraph.org"> taskgraph.org </a-typography-link>
          for more information.
        </a-typography-paragraph>
        <a-typography-paragraph>
          The TaskGraph project is an open source project management application that utilizes ideas
          from asynchronous programming, cooperative multitasking and git versioning to help you
          finish projects more efficiently.
        </a-typography-paragraph>
        <a-typography-paragraph>
          taskgraph-vue-antd is a submodule of TaskGraph that provides Web UI to communicate with
          the TaskGraph backend.
        </a-typography-paragraph>
      </a-typography>
    </a-layout-content>
    <a-layout-footer style="text-align: center">
      TaskGraph Web UI ©2024 taskgraph.org
    </a-layout-footer>
  </a-layout>
</template>
