import { defineStore } from 'pinia'
import { type RemovableRef, useStorage } from '@vueuse/core'
import { computed, type UnwrapRef, reactive } from 'vue'
import type { Dayjs } from 'dayjs'
// =============== Project List ================
// stores a list of projects, and metadata (status, name, etc.) for each project.
// K-V storage is used, each project can be looked-up by its UUID.

export interface ProjectListItem {
  name: string
}

export interface ProjectListState {
  projects: Record<string, ProjectListItem>
}

// This stores a list of user projects, which is synchronized with remote via RESTful or WebSocket
export const useProjectListStore = defineStore('taskgraph-project-list', () => {
  const projectListState: RemovableRef<ProjectListState> = useStorage(
    'taskgraph-project-list-local-storage',
    { projects: {} }
  )

  const number_of_projects = computed(() => Object.keys(projectListState.value.projects).length)

  return {
    projectListState,
    number_of_projects
  }
})

// =============== Dashboard Display ================
// stores a list of tasks looked up by status.
// K-V storage is used, each task and project can be looked-up by its UUID.

export interface TaskItem {
  name: string
  detail: string | null
}

export interface TaskListState {
  projects: Record<string, Record<string, TaskItem>>
}

// This stores a list of tasks filtered by different conditions
export const useTaskListStore = defineStore('taskgraph-task-list', () => {
  const activeTaskListState: RemovableRef<TaskListState> = useStorage(
    'taskgraph-active-task-list-local-storage',
    { projects: {} }
  )

  return {
    activeTaskListState
  }
})

// ============ Project Operation =================
// These stores store the states of the input widgets
// for managing projects and working on projects,
// such as name / theme color of new project,
// name / date of new task, etc.

export interface NewProjectInputState {
  name: string
}

export interface ProjectDagViewInputState {
  layout: string
}

export interface ProjectWorkspaceInputState {
  selected_node: string | null
  selected_edge: string | null
  previous_selected_node: string | null
  previous_selected_edge: string | null
  add_new_task_name: string
  add_new_task_detail: string
  task_toolbox_location_select: string
  add_dependency_selected_nodes: Array<string>
  snooze_task_until: Dayjs | null
}

// This store is for project operation inputs
export const useProjectOperationInputStore = defineStore(
  'taskgraph-project-operation-input',
  () => {
    const newProjectInputState: UnwrapRef<NewProjectInputState> = reactive({
      name: 'New Project'
    })
    const projectDagViewInputState: UnwrapRef<ProjectDagViewInputState> = reactive({
      layout: 'dagre'
    })
    const projectWorkspaceInputState: UnwrapRef<ProjectWorkspaceInputState> = reactive({
      selected_node: null,
      selected_edge: null,
      previous_selected_node: null,
      previous_selected_edge: null,
      add_new_task_name: '',
      add_new_task_detail: '',
      task_toolbox_location_select: 'sub',
      add_dependency_selected_nodes: [],
      snooze_task_until: null
    })
    return {
      newProjectInputState,
      projectDagViewInputState,
      projectWorkspaceInputState
    }
  }
)

// ============== Project Local Buffer ===============
// Stores the current projects data.
// should be automatically synchronized with remote.
// Localstorage is used so that next time user comes back,
//  there can be some content to display before loading remote resources.

export interface TaskGraphDAG {
  directed: boolean
  multigraph: boolean
  graph: object
  nodes: Array<{ id: string }>
  links: Array<{ id: string; source: string; target: string }>
}

export interface TaskGraphProjectData {
  name: string
  DAG: TaskGraphDAG
  metadata: Record<string, Record<string, string>>
}

export interface TaskGraphData {
  projects: Record<string, TaskGraphProjectData>
}

export const useTaskGraphDataStore = defineStore('taskgraph-data', () => {
  const taskgraphData: RemovableRef<TaskGraphData> = useStorage('taskgraph-data-local-storage', {
    projects: {}
  })
  return {
    taskgraphData
  }
})
