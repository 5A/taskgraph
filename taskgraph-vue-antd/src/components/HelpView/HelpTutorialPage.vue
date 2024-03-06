<template>
  <a-breadcrumb style="margin: 16px 0">
    <a-breadcrumb-item>Help</a-breadcrumb-item>
    <a-breadcrumb-item>Tutorial</a-breadcrumb-item>
  </a-breadcrumb>
  <a-layout-content
    :style="{
      background: '#fff',
      padding: '24px',
      margin: 0,
      minHeight: '280px'
    }"
  >
    <a-typography>
      <a-typography-title :level="2">Tutorial</a-typography-title>
      <a-typography-paragraph> [TODO] </a-typography-paragraph>
    </a-typography>
    <a-card title="Button Types">
      <a-row :gutter="[16, 8]">
        <a-col>
          <a-button type="default" @click="onWhiteButtonClick"> No Consequences </a-button>
        </a-col>
        <a-col>
          <a-button type="primary" @click="onBlueButtonClick">
            {{ blue_button_text }}
          </a-button>
        </a-col>
        <a-col>
          <a-button type="primary" style="background-color: #f0ad4e" @click="onOrangeButtonClick">
            Real World Action
          </a-button>
        </a-col>
        <a-col>
          <a-button type="default" danger @click="onDangerButtonClick">
            {{ danger_button_text }}
          </a-button>
        </a-col>
        <a-col>
          <a-button type="primary" danger @click="onRedButtonClick"> Dangerous Action </a-button>
          <a-modal
            v-model:open="red_button_confirm_open"
            title="Are you sure?"
            okText="YES!"
            @ok="handleOk"
            @cancel="handleCancel"
          >
            <p>This button clearly says "Dangerous Action".</p>
            <p>Are you sure you want to push the button?</p>
          </a-modal>
        </a-col>
        <a-col>
          <a-button type="primary" style="background-color: #5cb85c"> Long Task </a-button>
        </a-col>
        <a-col>
          <a-button type="primary" style="background-color: #5bc0de"> Special </a-button>
        </a-col>
      </a-row>
    </a-card>
  </a-layout-content>
</template>

<script lang="ts" setup>
import { message } from 'ant-design-vue'
import { ref } from 'vue'

const no_consequence_texts = [
  'Click again!',
  'Click more!',
  'Just click it!',
  'Click it!',
  'Cookie clicker!'
]

const onWhiteButtonClick = () => {
  message.info(no_consequence_texts[Math.floor(Math.random() * no_consequence_texts.length)])
}

const blue_button_text = ref<string>('Change Data')
const onBlueButtonClick = () => {
  if (blue_button_text.value == 'Change Data') {
    blue_button_text.value = 'Data Change'
  } else {
    blue_button_text.value = 'Change Data'
  }
}

const onOrangeButtonClick = () => {
  message.info('Imagine your room light is now turned on/off')
}

const danger_button_text = ref<string>('Irreversible')
const onDangerButtonClick = () => {
  danger_button_text.value = 'I told you'
}

const red_button_confirm_open = ref<boolean>(false)

const showModal = () => {
  red_button_confirm_open.value = true
}

const handleOk = () => {
  red_button_confirm_open.value = false
  message.warn('Imagine your lab just blew up.')
}

const handleCancel = () => {
  red_button_confirm_open.value = false
  message.info('You are clever.')
}

const onRedButtonClick = () => {
  showModal()
}
</script>
