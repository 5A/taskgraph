<template>
  <a-layout-content
    :style="{
      background: '#fff',
      padding: '24px',
      margin: '24px 0 24px 0',
      minHeight: '280px'
    }"
  >
    <a-flex gap="small">
      <a-card title="DAG View" style="width: 70%">
        <template #extra>
          <a-flex gap="small">
            <a-select
              ref="select"
              v-model:value="projectOperationInputStore.projectDagViewInputState.layout"
              style="width: 120px"
              :options="cytoscapeLayoutOptions"
              @change="handleCytoscapeLayoutSelectChange"
            ></a-select>
            <a-button @click="onResetDAGView"> Reset View </a-button>
          </a-flex>
        </template>
        <div class="cytoscape-container" ref="cytoscapeContainer"></div>
      </a-card>
      <a-card title="Task Toolbox" style="width: 30%">
        <a-form :model="projectInputState" layout="vertical">
          <a-form-item label="Name">
            <a-input
              v-model:value="projectInputState.add_new_task_name"
              style="width: 100%"
              placeholder="Task Name"
            />
          </a-form-item>
          <a-form-item label="Detail">
            <a-textarea
              v-model:value="projectInputState.add_new_task_detail"
              placeholder="Description of task"
              :rows="4"
            />
          </a-form-item>
          <a-form-item label="Relationship to Selected Task">
            <a-radio-group
              v-model:value="projectInputState.task_toolbox_location_select"
              style="width: 100%"
            >
              <a-radio-button value="sub">Sub-task</a-radio-button>
              <a-radio-button value="super">Super-task</a-radio-button>
              <a-radio-button value="self">Self</a-radio-button>
            </a-radio-group>
          </a-form-item>
          <a-form-item>
            <a-flex gap="small" wrap="wrap">
              <a-button type="primary" @click="onAddOrModifyTask">
                <PlusCircleOutlined /> Add/Modify Task
              </a-button>
              <a-button danger @click="onClearNewTaskInput"> Clear </a-button>
            </a-flex>
          </a-form-item>
          <a-divider />
          <a-form-item label="Depends On">
            <a-select
              v-model:value="projectInputState.add_dependency_selected_nodes"
              mode="tags"
              style="width: 100%"
              placeholder="Select Dependency"
              optionFilterProp="label"
              :options="selectOptionsOfTasks"
            ></a-select>
          </a-form-item>
          <a-form-item>
            <a-flex gap="small" wrap="wrap">
              <a-button type="primary" @click="onAddDependencies">
                <PlusCircleOutlined /> Add Dependencies
              </a-button>
              <a-button danger @click="onRemoveDependency"> Remove Selected </a-button>
            </a-flex>
          </a-form-item>
        </a-form>
      </a-card>
    </a-flex>
    <br />
    <a-card :title="`Task: ${selectedTaskName}`" style="width: 100%">
      <template #extra>
        <a-flex gap="small">
          <a-button key="1" @click="onSetTaskDone" type="primary">
            <CheckCircleOutlined />
            Done
          </a-button>
          <a-button key="2" type="primary" danger @click="onRemoveTask">
            <DeleteOutlined />
            Remove
          </a-button>
        </a-flex>
      </template>
      <pre>{{ selectedTaskDetail }}</pre>
    </a-card>
  </a-layout-content>
  <a-page-header
    class="project-page-header"
    style="border: 1px solid rgb(235, 237, 240)"
    :title="projectName"
    :sub-title="projectUUID"
  >
    <template #extra>
      <a-button key="1" type="primary" @click="onSyncStatus">
        <SyncOutlined />
        Sync
      </a-button>
      <a-button key="2" type="primary" danger @click="showDeleteProjectModal">
        <DeleteOutlined />
        Delete
      </a-button>
    </template>
    <a-descriptions size="small" :column="{ xxl: 8, xl: 6, lg: 6, md: 4, sm: 2, xs: 2 }">
      <a-descriptions-item label="Total Tasks"> {{ numberOfTasks }} </a-descriptions-item>
      <a-descriptions-item label="Done"> {{ projectTaskStatistics.done }} </a-descriptions-item>
      <a-descriptions-item label="Active"> {{ projectTaskStatistics.active }} </a-descriptions-item>
      <a-descriptions-item label="Pending">
        {{ projectTaskStatistics.pending }}
      </a-descriptions-item>
      <a-descriptions-item label="Snoozed">
        {{ projectTaskStatistics.snoozed }}
      </a-descriptions-item>
      <a-descriptions-item label="Unknown Status">
        {{ projectTaskStatistics.unknown }}
      </a-descriptions-item>
      <a-descriptions-item label="Stated Tasks">
        {{ projectTaskStatistics.total }}
      </a-descriptions-item>
    </a-descriptions>
    <a-modal
      v-model:open="deleteProjectModalOpen"
      title="Delete This Project?"
      @ok="handleDeleteProjectModalOk"
    >
      <p>Name: {{ projectName }}</p>
      <p>UUID: {{ projectUUID }}</p>
    </a-modal>
  </a-page-header>
</template>

<script lang="ts" setup>
// Vue and vue ecosystem
import { computed, ref, watch, onMounted, toRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// Theme
import { message } from 'ant-design-vue'
import type { SelectProps } from 'ant-design-vue'
import {
  CheckCircleOutlined,
  DeleteOutlined,
  SyncOutlined,
  PlusCircleOutlined
} from '@ant-design/icons-vue'
// Graph plotting
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'
// This project
import {
  useProjectListStore,
  useTaskGraphDataStore,
  useProjectOperationInputStore
} from '@/store/projects'
import { callRESTfulAPI } from '@/common/connection'
import { type TaskGraphProjectData } from '@/store/projects'

cytoscape.use(dagre)

const route = useRoute()
const router = useRouter()
const projectListStore = useProjectListStore()
const taskgraphDataStore = useTaskGraphDataStore()
const projectOperationInputStore = useProjectOperationInputStore()

async function readProject(project_uuid: string) {
  // get project data for given uuid
  await callRESTfulAPI(`projects/${project_uuid}`, 'GET').then((response) => {
    if (response?.name) {
      taskgraphDataStore.taskgraphData.projects[project_uuid] = response
    }
  })
}

const projectUUID = ref<string>()
if (typeof route.params.project_uuid === 'string') {
  projectUUID.value = route.params.project_uuid
}

// ======== Aliases for Convenience ===========
const currentProject = computed(() =>
  projectUUID.value ? taskgraphDataStore.taskgraphData.projects[projectUUID.value] : null
)
const projectName = computed(() =>
  currentProject.value ? currentProject.value.name : 'Loading...'
)
const listOfTasks = computed(() =>
  currentProject.value ? currentProject.value.DAG.nodes.map((item) => item.id) : null
)
const numberOfTasks = computed(() => (listOfTasks.value ? listOfTasks.value.length : null))
const selectOptionsOfTasks = computed(() =>
  listOfTasks.value
    ? listOfTasks.value.map((item) => ({
        value: item,
        label: currentProject.value?.metadata[item]['Name']
      }))
    : null
)
const projectTaskStatistics = computed(() => {
  let n_tasks_done = 0
  let n_tasks_active = 0
  let n_tasks_pending = 0
  let n_tasks_snoozed = 0
  let n_tasks_unknown_status = 0
  if (currentProject.value && currentProject.value.metadata) {
    for (const item in currentProject.value.metadata) {
      const meta = currentProject.value.metadata[item]
      if ('Status' in meta) {
        const task_status = meta['Status']
        if (task_status === 'Done') {
          n_tasks_done++
        } else if (task_status === 'Active') {
          n_tasks_active++
        } else if (task_status === 'Pending') {
          n_tasks_pending++
        } else if (task_status === 'Snoozed') {
          n_tasks_snoozed++
        } else {
          n_tasks_unknown_status++
        }
      }
    }
  }
  return {
    done: n_tasks_done,
    active: n_tasks_active,
    pending: n_tasks_pending,
    snoozed: n_tasks_snoozed,
    unknown: n_tasks_unknown_status,
    total: n_tasks_done + n_tasks_active + n_tasks_pending + n_tasks_snoozed
  }
})

// ======== React to router parameter changes when loading project page
onMounted(() => {
  if (typeof route.params.project_uuid === 'string') {
    projectUUID.value = route.params.project_uuid
    readProject(projectUUID.value).then(() => initCytoscape())
    projectInputState.selected_node = null
    projectInputState.add_dependency_selected_nodes = []
  }
})

watch(
  () => route.params.project_uuid,
  (newId, oldId) => {
    if (typeof newId === 'string') {
      projectUUID.value = newId
      readProject(projectUUID.value).then(() => initCytoscape())
      projectInputState.selected_node = null
      projectInputState.add_dependency_selected_nodes = []
    }
  }
)

// ========== Button callbacks

const deleteProjectModalOpen = ref<boolean>(false)

const showDeleteProjectModal = () => {
  deleteProjectModalOpen.value = true
}

const handleDeleteProjectModalOk = (e: MouseEvent) => {
  deleteProject()
  deleteProjectModalOpen.value = false
}

async function deleteProject() {
  // Delete project by DELETE
  await callRESTfulAPI(
    'projects',
    'DELETE',
    JSON.stringify({
      uuid: projectUUID.value
    })
  ).then((response) => {
    if (response?.id) {
      console.log('Project Deleted')
    }
  })
  // Purge records locally, resync with remote
  // retrive a list of projects by GET
  await callRESTfulAPI('projects', 'GET').then((response) => {
    if (response?.projects) {
      projectListStore.projectListState.projects = {}
      for (const item in response.projects) {
        projectListStore.projectListState.projects[item] = response.projects[item]
      }
    }
  })
  // Navigate user to landing page
  router.push({ path: '/projects/manage' })
}

async function onSyncStatus() {
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

// ========== Cytoscape Render ========
const cytoscapeLayoutOptions = ref<SelectProps['options']>([
  {
    value: 'dagre',
    label: 'Dagre'
  },
  {
    value: 'breadthfirst',
    label: 'Breadth First'
  },
  {
    value: 'cose',
    label: 'CoSE'
  },
  {
    value: 'circle',
    label: 'Circle'
  },
  {
    value: 'concentric',
    label: 'Concentric'
  },
  {
    value: 'random',
    label: 'Random'
  }
])

// construct cytoscape data from taskgraph data, if got null/undefined, empty data is generated.
function construct_cytoscape_data(tgdata: TaskGraphProjectData | null) {
  let nodes = []
  let edges = []
  if (tgdata) {
    for (const item of tgdata.DAG.nodes) {
      let data: Record<string, string> = { id: item.id }
      if (item.id in tgdata.metadata) {
        if ('Name' in tgdata.metadata[item.id]) {
          data['name'] = tgdata.metadata[item.id]['Name']
        }
        if ('Status' in tgdata.metadata[item.id]) {
          data['status'] = tgdata.metadata[item.id]['Status']
        }
      }
      nodes.push({
        data: data
      })
    }
    for (const item of tgdata.DAG.links) {
      edges.push({
        data: { id: item.id, source: item.source, target: item.target }
      })
    }
  }
  return {
    nodes: nodes,
    edges: edges
  }
}

function get_status_color(ele: any): any {
  const status: string = ele.data('status')
  if (status === 'Active') {
    return '#5bc0de'
  } else if (status === 'Pending') {
    return '#FFFFFF'
  } else if (status === 'Done') {
    return '#000000'
  } else if (status === 'Snoozed') {
    return '#5cb85c'
  } else {
    return '#00FF00'
  }
}

// we cannot use Array<cytoscape.Stylesheet> because we are using mapping functions,
// which breaks the type notations of cytoscape... so we just use any here
function get_cytoscape_style(): any {
  let node_basic_style = {
    // basic shape
    shape: 'round-tag',
    height: '20px',
    width: '20px',
    'background-color': get_status_color,
    // boarder
    'border-width': 2,
    'border-style': 'solid',
    'border-color': '#000000',
    // padding
    padding: '0px',
    // label
    label: 'data(name)',
    'font-family': 'Arial, SimHei',
    'font-size': 18,
    'font-weight': 'normal',
    'text-halign': 'right',
    'text-valign': 'center',
    'text-margin-x': '4px',
    'text-background-padding': '2px',
    'text-border-opacity': 0.2,
    'text-border-width': 2,
    'text-border-color': '#000000'
  }
  let node_style = { ...node_basic_style }
  let node_selected_style = { ...node_basic_style }
  node_selected_style['background-color'] = () => '#FF4D4F'
  let edge_basic_style = {
    width: 3,
    'line-color': '#CCCCCC',
    'target-arrow-color': '#CCCCCC',
    'target-arrow-shape': 'triangle',
    'arrow-scale': 1.5,
    'curve-style': 'bezier'
  }
  let edge_style = { ...edge_basic_style }
  let edge_selected_style = { ...edge_basic_style }
  edge_selected_style['line-color'] = '#333333'
  edge_selected_style['target-arrow-color'] = '#333333'
  let export_style = [
    {
      selector: 'node',
      style: node_style
    },
    {
      selector: 'node.selected',
      style: node_selected_style
    },
    {
      selector: 'edge',
      style: edge_style
    },
    {
      selector: 'edge.selected',
      style: edge_selected_style
    }
  ]
  return export_style
}

function get_cytoscape_layout(): any {
  return {
    name: projectOperationInputStore.projectDagViewInputState.layout,
    nodeDimensionsIncludeLabels: true // for Dagre
  }
}

const cytoscapeContainer = ref(null)
const cytoscapeInstance = ref<cytoscape.Core>()

const initCytoscape = () => {
  if (cytoscapeContainer.value === null) {
    // Component not loaded yet, call this later.
    return
  }
  console.log('Cytoscape initialized.')
  cytoscapeInstance.value = cytoscape({
    container: cytoscapeContainer.value,
    elements: construct_cytoscape_data(currentProject.value),
    style: get_cytoscape_style(),
    layout: get_cytoscape_layout(),
    minZoom: 0.1,
    maxZoom: 2.0
  })
  cytoscapeInstance.value.on('tap', 'node', function (evt) {
    var node = evt.target
    projectInputState.previous_selected_node = projectInputState.selected_node
    projectInputState.selected_node = node.id()
    if (projectInputState.previous_selected_node) {
      cytoscapeInstance.value?.$id(projectInputState.previous_selected_node).removeClass('selected')
    }
    node.addClass('selected')
  })
  cytoscapeInstance.value.on('tap', 'edge', function (evt) {
    var edge = evt.target
    projectInputState.previous_selected_edge = projectInputState.selected_edge
    projectInputState.selected_edge = edge.id()
    if (projectInputState.previous_selected_edge) {
      cytoscapeInstance.value?.$id(projectInputState.previous_selected_edge).removeClass('selected')
    }
    edge.addClass('selected')
  })
}

// ========== TaskGraph Logic =========
const projectInputState = projectOperationInputStore.projectWorkspaceInputState

function get_selected_task_meta() {
  if (!currentProject.value) {
    return null
  }
  if (!projectInputState.selected_node) {
    return null
  }
  if (!(projectInputState.selected_node in currentProject.value.metadata)) {
    return null
  }
  return currentProject.value.metadata[projectInputState.selected_node]
}

const selectedTaskName = computed(() => {
  let meta = get_selected_task_meta()
  return meta ? meta['Name'] : 'No Task Selected'
})

const selectedTaskDetail = computed(() => {
  let meta = get_selected_task_meta()
  return meta ? meta['Detail'] ?? 'No Detail Available' : 'No Detail Available'
})

async function handleCytoscapeLayoutSelectChange() {
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onResetDAGView() {
  cytoscapeInstance.value?.reset()
}

async function onAddOrModifyTask() {
  if (projectInputState.task_toolbox_location_select === 'sub') {
    await onAddSubTask()
  } else if (projectInputState.task_toolbox_location_select === 'super') {
    await onAddSuperTask()
  }
}

async function onAddSubTask() {
  if (projectInputState.selected_node) {
    await callRESTfulAPI(
      `projects/${projectUUID.value}`,
      'POST',
      JSON.stringify({
        add_sub_task: {
          parent: projectInputState.selected_node,
          name: projectInputState.add_new_task_name,
          detail: projectInputState.add_new_task_detail
        }
      })
    ).then((response) => {
      if (response?.result == 'OK') {
        message.info('New sub-task created')
      }
    })
  } else {
    message.error(
      'Please select a parent task for the new task before adding \
      (click a task in the DAG View to select it)'
    )
  }
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onAddSuperTask() {
  if (projectInputState.selected_node) {
    await callRESTfulAPI(
      `projects/${projectUUID.value}`,
      'POST',
      JSON.stringify({
        add_super_task: {
          child: projectInputState.selected_node,
          name: projectInputState.add_new_task_name,
          detail: projectInputState.add_new_task_detail
        }
      })
    ).then((response) => {
      if (response?.result == 'OK') {
        message.info('New super-task created')
      }
    })
  } else {
    message.error(
      'Please select a child task for the new task before adding \
      (click a task in the DAG View to select it)'
    )
  }
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onClearNewTaskInput() {
  projectInputState.add_new_task_detail = ''
  projectInputState.add_new_task_name = ''
}

async function onSetTaskDone() {
  if (projectInputState.selected_node) {
    await callRESTfulAPI(
      `projects/${projectUUID.value}`,
      'POST',
      JSON.stringify({
        update_task_status: {
          uuid: projectInputState.selected_node,
          status: 'Done'
        }
      })
    ).then((response) => {
      if (response?.result == 'OK') {
        message.info('Task marked as done')
      }
    })
  } else {
    message.error(
      'Please select a task before the operation \
      (click a task in the DAG View to select it)'
    )
  }
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onRemoveTask() {
  if (projectInputState.selected_node) {
    await callRESTfulAPI(
      `projects/${projectUUID.value}`,
      'POST',
      JSON.stringify({
        remove_task: {
          uuid: projectInputState.selected_node
        }
      })
    ).then((response) => {
      if (response?.result == 'OK') {
        message.warning('Task removed')
      }
    })
  } else {
    message.error(
      'Please select a task before the operation \
      (click a task in the DAG View to select it)'
    )
  }
  projectInputState.selected_node = null
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onAddDependencies() {
  if (projectInputState.selected_node && projectInputState.add_dependency_selected_nodes) {
    await callRESTfulAPI(
      `projects/${projectUUID.value}`,
      'POST',
      JSON.stringify({
        add_dependencies: {
          uuid: projectInputState.selected_node,
          dependencies: projectInputState.add_dependency_selected_nodes
        }
      })
    ).then((response) => {
      if (response?.result == 'OK') {
        message.warning('Dependencies added')
      }
    })
  } else {
    message.error(
      'Please select the task and dependencies before the operation \
      (click a task in the DAG View to select it as dependent, \
      select dependencies in the Task Toolbox)'
    )
  }
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onRemoveDependency() {
  if (projectInputState.selected_edge) {
    const selected_edge = cytoscapeInstance.value?.$id(projectInputState.selected_edge)
    if (selected_edge) {
      await callRESTfulAPI(
        `projects/${projectUUID.value}`,
        'POST',
        JSON.stringify({
          remove_dependency: {
            uuid_super_task: selected_edge.target().id(),
            uuid_sub_task: selected_edge.source().id()
          }
        })
      ).then((response) => {
        if (response?.result == 'OK') {
          message.warning('Dependency removed')
        }
      })
    } else {
      console.error('Unexpected: selected edge does not exist in cytoscape data')
      console.log(projectInputState.selected_edge)
    }
  } else {
    message.error(
      'Please select an edge before the operation \
      (click an edge in the DAG View to select it)'
    )
  }
  projectInputState.selected_edge = null
  if (projectUUID.value) await readProject(projectUUID.value).then(() => initCytoscape())
}

async function onSnoozeTask() {}

async function onChangeTaskStatus() {}

async function onEditTaskName() {}

async function onEditTaskDetail() {}
</script>

<style scoped>
.project-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
.project-page-header :deep(tr:last-child td) {
  padding-bottom: 0;
}
.cytoscape-container {
  width: 100%;
  height: 500px;
}
</style>
