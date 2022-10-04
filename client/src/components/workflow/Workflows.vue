<template>
  <div>
    <div v-if="waiting">
      <span class="icon is-medium is-size-4">
        <i class="fas fa-spinner fa-pulse"></i>
      </span>
    </div>
    <div v-else>
      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>

      <address-bar />

      <div class="mt-4">
        <div class="buttons is-pulled-right">
          <router-link v-if="this.configId == this.folderId" :to="'/org/' + orgId + '/new-workflow/' + this.configId + '/' + this.folderId + '/new'" class="button">
            <span class="icon">
              <i class="fas fa-plus"></i>
            </span>
            <span v-if="orgWorkflowConfig && orgWorkflowConfig.creationButton">{{orgWorkflowConfig.creationButton}}</span>
            <span v-else>New Workflow</span>
          </router-link>
        </div>
        <h1 class="title is-4">
          <span class="my-folder-name">{{folderName}}</span>
          <div class="dropdown is-hoverable ml-3" v-if="isAdmin">
            <div class="dropdown-trigger">
              <button class="button" aria-haspopup="true" aria-controls="dropdown-menu">
                <span class="icon">
                  <i class="fas fa-folder"></i>
                </span>
                <span class="icon is-small">
                  <i class="fas fa-angle-down" aria-hidden="true"></i>
                </span>
              </button>
            </div>
            <div class="dropdown-menu" id="dropdown-menu" role="menu">
              <div class="dropdown-content">
                <router-link class="dropdown-item" v-for="(f, i) in subfolders" :key="'menu-subfolder-'+i" :to="'/org/' + orgId + '/workflow-folder/' + configId + '/' + f.id">
                  <span class="icon">
                    <i class="fas fa-folder"></i>
                  </span>
                  <span>{{f.name}}</span>
                </router-link>
                <hr class="dropdown-divider" v-if="subfolders.length" />
                <a class="dropdown-item" v-if="!isRootFolder" @click="openFolderModal(folder)">
                  Edit this folder
                </a>
                <hr class="dropdown-divider" v-if="!isRootFolder">
                <a class="dropdown-item" @click="openFolderModal(null)">
                  Add new folder
                </a>
                <hr class="dropdown-divider" v-if="selectedWorkflows && selectedWorkflows.length">
                <a class="dropdown-item" v-if="selectedWorkflows && selectedWorkflows.length" @click="openMoveWorkflowModal">
                  Move selected {{selectedWorkflows.length}} workflows
                </a>
                <hr class="dropdown-divider">
                <a class="dropdown-item" @click="openExportWorkflowModal(false)">
                  Export workflows
                </a>
                <a class="dropdown-item" @click="openExportWorkflowModal(true)" v-if="selectedWorkflows.length">
                  Export selected {{selectedWorkflows.length}} workflows
                </a>
              </div>
            </div>
          </div>
        </h1>
        <h2 class="subtitle is-6">&nbsp;</h2>
      </div>
  
      <div v-if="workflows">
        
        <div class="columns mt-4">
          <div class="column field mb-0 pb-0">
            <p class="control has-icons-left">
              <span class="select">
                <select v-model="localFilter">
                  <option v-for="(opt, i) in workflowFilterOptions" :key="'workflowFilterOption-'+i">{{opt}}</option>
                </select>
              </span>
              <span class="icon is-small is-left">
                <i class="fas fa-filter"></i>
              </span>
            </p>
          </div>
          <div class="column field  mb-0 pb-0">
            <p class="control has-icons-left">
              <input class="input" type="text" placeholder="Search" v-model="search">
              <span class="icon is-small is-left">
                <i class="fas fa-search"></i>
              </span>
            </p>
          </div>
        </div>

        <div v-if="workflows.length">
          <table class="table is-fullwidth is-hoverable is-striped">
            <thead>
              <tr>
                <th v-if="isAdmin">
                  <label class="checkbox">
                    <input type="checkbox" v-model="selectedAll" />
                  </label>
                </th>
                <th class="is-clickable" @click="changeSortOption('id')">
                  <span>Id</span>
                  <span class="icon" v-if="sortOption.field == 'id'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
                <th class="is-clickable" @click="changeSortOption('state')">
                  <span>State</span>
                  <span class="icon" v-if="sortOption.field == 'state'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
                <th v-for="(f, i) in dashboardFields" :key="'wfth' + i" class="is-clickable" @click="changeSortOption(f.name)" :class="{'has-text-right': f.type=='number'}">
                  <span>{{f.label}}</span>
                  <span class="icon" v-if="sortOption.field == f.name">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
                <th class="is-clickable" @click="changeSortOption('createdBy')">
                  <span>Created By</span>
                  <span class="icon" v-if="sortOption.field == 'createdBy'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
                <th class="is-clickable" @click="changeSortOption('createdAt')">
                  <span>Created At</span>
                  <span class="icon" v-if="sortOption.field == 'createdAt'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
                <!--<th class="is-clickable" @click="changeSortOption('updatedAt')">
                  <span>Updated At</span>
                  <span class="icon" v-if="sortOption.field == 'updatedAt'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>-->
              </tr>
            </thead>
            <tbody>
              <tr class="is-clickable" v-for="(w, i) in showingWorkflows" :key="'wftbr-' + i" @click="viewWorkflow(w)">
                <td v-if="isAdmin" @click.stop="''">
                  <label class="checkbox">
                    <input type="checkbox" v-model="selection[w.id]" />
                  </label>
                </td>
                <td>{{w.id}}</td>
                <td>
                  <span class="tag is-link" :style="{'background-color': w.stateColor}">{{w.state}}</span>
                </td>
                <td v-for="(f, j) in dashboardFields" :key="'wftb-r-' + i + '-c-' + j" :class="{'has-text-right': f.type=='number'}">
                  <span v-if="f.type=='number' && f.twoDigits">{{Number(w[f.name]).toLocaleString('en-US', {maximumFractionDigits: 2, minimumFractionDigits: 2, useGrouping: false})}}</span>
                  <span v-else>{{w[f.name]}}</span>
                </td>
                <td>{{w.createdBy}}</td>
                <td>{{w.createdAtLabel}}</td>
                <!--<td>{{w.updatedAtLabel}}</td>-->
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else>
          <article class="message is-info">
            <div class="message-body">
              No workflows found.
            </div>
          </article>
        </div>

        <folder-modal :opened="folderModal.opened" :folder="folderModal.folder" :canDelete="folderModal.canDelete" :parentId="folderId"
          @folder-modal-closed="folderModal.opened = false" />

        <move-workflow-modal :opened="moveWorkflowModal.opened" :folder="folder" :workflows="selectedWorkflows"
          @move-workflow-modal-closed="closeMoveWorkflowModal"/>

        <export-workflow-modal :opened="exportWorkflowModal.opened" :workflows="exportWorkflowModal.workflows" :fields="this.orgWorkflowConfig && this.orgWorkflowConfig.fields"
          @export-workflow-modal-closed="closeExportWorkflowModal"/>

      </div>
    </div>
  </div>
</template>

<script>
import dateFormat from 'dateformat'
import FolderModal from '@/components/modals/FolderModal'
import MoveWorkflowModal from '@/components/modals/MoveWorkflowModal'
import ExportWorkflowModal from '@/components/modals/ExportWorkflowModal'
import AddressBar from '@/components/workflow/AddressBar'

export default {
  name: 'Workflows',
  components: {
    FolderModal,
    MoveWorkflowModal,
    ExportWorkflowModal,
    AddressBar
  },
  data () {
    return {
      error: '',
      waiting: false,
      workflows: null,
      workflowLength: 0,
      workflowFilterOptions: ['All'],
      localFilter: 'All',
      search: '',
      sortOption: {
        field: 'createdAt',
        asc: false
      },
      selection: {},
      selectedAll: false,
      folderModal: {
        opened: false,
        folder: null,
        canDelete: false,
        parentId: null,
      },
      moveWorkflowModal: {
        opened: false,
      },
      exportWorkflowModal: {
        opened: false,
        workflows: [],
      },
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    workflowFilter () {
      return this.$store.state.config.workflowFilter
    },
    email () {
      return this.$store.state.user.email
    },
    orgId () {
      return this.$route.params.orgId
    },
    configId () {
      return this.$route.params.configId
    },
    folderId () {
      return this.$route.params.folderId
    },
    org () {
      return this.$store.state.org.org
    },
    orgUsers () {
      return this.$store.state.org.orgUsers
    },
    orgUsersMap () {
      if (!this.orgUsers) {
        return {}
      }
      var result = {}
      for (const u of this.orgUsers) {
        result[u.email] = u
      }
      return result
    },
    orgUser () {
      if (!this.email || !this.orgUsers) {
        return null
      }
      var email = this.email
      return this.orgUsers.filter(function(u){
        return u.email == email
      })[0]
    },
    isAdmin () {
      if (!this.orgUser) {
        return false
      }
      if (!this.orgWorkflowConfig || !this.orgWorkflowConfig.adminGroup) {
        return false
      }
      return this.orgUser.groups.includes(this.orgWorkflowConfig.adminGroup)
    },
    orgWorkflowConfigs () {
      return this.$store.state.org.orgWorkflowConfigs
    },
    orgWorkflowConfig () {
      if (!this.orgWorkflowConfigs) {
        return null
      }
      for(const workflowConfig of this.orgWorkflowConfigs) {
        if (workflowConfig.id == this.configId) {
          return workflowConfig
        }
      }
      return null
    },
    stateColorMap () {
      var stateColorMap = {}
      if (!this.orgWorkflowConfig) {
        return stateColorMap
      }
      for (const state of this.orgWorkflowConfig.states) {
        stateColorMap[state.name] = state.color
      }
      return stateColorMap
    },
    dashboardFields () {
      if (!this.orgWorkflowConfig) {
        return []
      }
      var dashboardFields = this.orgWorkflowConfig.fields.filter(f => f.dashboard)
      dashboardFields.sort((a, b) => a.dashboard - b.dashboard)
      return dashboardFields
    },
    isRootFolder () {
      return this.orgWorkflowConfig && this.folderId == this.orgWorkflowConfig.id
    },
    showingWorkflows () {
      var orgUsersMap = this.orgUsersMap
      var fields = this.orgWorkflowConfig ? this.orgWorkflowConfig.fields : []
      var colorMap = this.stateColorMap
      var mappedWorkflows = this.workflows.map(w => {
        var copy = JSON.parse(JSON.stringify(w))
        var createdBy = orgUsersMap[w.createdBy]
        copy.createdBy = (createdBy && createdBy.username) ? createdBy.username : w.createdBy
        for (const f of fields) {
          if (typeof(f.options) == 'string') {
            if (f.type == 'string') {
              var orgUser = orgUsersMap[w[f.name]]
              copy[f.name] = (orgUser && orgUser.username) ? orgUser.username : w[f.name]
            }
            if (f.type == 'strings' && Array.isArray(w[f.name])) {
              copy[f.name] = w[f.name].map(e => {
                var u = orgUsersMap[e]
                return (u && u.username) ? u.username : e
              })
            }
          }
        }
        copy.stateColor = colorMap[w.state] ? colorMap[w.state] : '#485fc7'
        return copy
      })
      var search = this.search.trim().toLowerCase()
      var workflowFilter = this.localFilter
      var filteredWorkflows = mappedWorkflows.filter(w => {
        if (workflowFilter != 'All' && w.state != workflowFilter) {
          return false
        }
        for(const f of this.dashboardFields) {
          var val = w[f.name] ? w[f.name].toString().toLowerCase() : ''
          if (val.includes(this.search)) {
            return true
          }
        }
        return w.id.includes(search)
          || w.state.toLowerCase().includes(search)
          || w.createdBy.toLowerCase().includes(search)
      })
      var sort = this.sortOption
      var sortFieldType = 'string'
      if (this.dashboardFields) {
        for (const df of this.dashboardFields) {
          if (df.name == sort.field) {
            if (df.type == 'number') {
              sortFieldType = 'number'
            }
            break
          }
        }
      }
      var sortedWorkflows = filteredWorkflows.sort((a, b) => {
        var va = a[sort.field]
        var vb = b[sort.field]
        if (sort.field == 'createdAt' || sort.field == 'id' || sortFieldType == 'number') {
          return sort.asc ? Number(va) - Number(vb) : Number(vb) - Number(va)
        }
        va = va ? va.toString() : ''
        vb = vb ? vb.toString() : ''
        return sort.asc ? va.localeCompare(vb) : vb.localeCompare(va)
      })
      return sortedWorkflows.map(w => {
        if (w.createdAt) {
          w.createdAtLabel = dateFormat(new Date(w.createdAt), 'mm/dd/yyyy')
        }
        if (w.updatedAt) {
          w.updatedAtLabel = dateFormat(new Date(w.updatedAt), 'mm/dd/yyyy')
        }
        return w
      })
    },
    selectedWorkflows () {
      if (!this.workflows) {
        return []
      }
      return this.workflows.filter(w => this.selection[w.id])
    },
    folderMap () {
      return this.$store.state.folders.folderMap
    },
    folder () {
      if (this.folderMap) {
        return this.folderMap[this.folderId]
      }
    },
    folderName () {
      if (this.folderId == this.configId) {
        return this.orgWorkflowConfig && this.orgWorkflowConfig.name
      }
      return this.folder && this.folder.name
    },
    subfolders () {
      if (!this.folderMap) {
        return []
      }
      var folders = []
      for (const folderId in this.folderMap) {
        var folder = this.folderMap[folderId]
        if (folder.parentId == this.folderId) {
          folders.push(folder)
        }
      }
      return folders
    },
  },
  watch: {
    configId: function (val) {
      this.getFolders()
    },
    folderId: function (val) {
      this.selectedAll = false
      this.getWorkflowsInFolder()
      this.localFilter = 'All'
    },
    selectedAll: function (val) {
      if (val) {
        for (const w of this.showingWorkflows) {
          this.selection[w.id] = true
        }
      } else {
        for (const i in this.selection) {
          this.selection[i] = false
        }
      }
    },
    localFilter: function (val) {
      this.$store.commit('config/setWorkflowFilter', val)
    },
  },
  methods: {
    getWorkflowsInFolder () {
      this.waiting = true
      this.$http.post(this.server + '/org/get-org-workflows-in-folder/' + this.folderId + '/', this.orgWorkflowConfig).then(resp => {
        this.workflows = this.processWorkflows(resp.body)
        this.waiting = false
      }, err => {
        console.log('Failed to get workflows')
        this.waiting = false
      })
    },
    viewWorkflow (w) {
      this.$router.push('/org/' + this.orgId + '/workflow/' + this.configId + '/' + w.id)
    },
    changeSortOption (name) {
      if (this.sortOption.field == name) {
        this.sortOption.asc = !this.sortOption.asc
      } else {
        this.sortOption.field = name
        this.sortOption.asc = true
      }
    },
    processWorkflows (workflows) {
      var processed = []
      var selection = {}
      var workflowLength = 0
      var workflowStates = []
      for (var w of workflows) {
        workflowLength = workflowLength + 1
        selection[w.id] = false
        var fieldPermissions = this.getFieldPermissions(w)
        if (!fieldPermissions) {
          continue
        }
        var viewable = false
        for (const f of this.dashboardFields) {
          if(fieldPermissions[f.name]['View']) {
            viewable = true
          } else {
            w[f.name] = '...'
          }
        }
        if (viewable) {
          processed.push(w)
          if (!workflowStates.includes(w.state)) {
            workflowStates.push(w.state)
          }
        }
      }
      this.selection = selection
      this.workflowLength = workflowLength
      if (!workflowStates.includes(this.localFilter)) {
        this.localFilter = 'All'
      }
      this.workflowFilterOptions = ['All'].concat(workflowStates)
      return processed
    },
    getFieldPermissions (w) {
      var stateConfig = this.orgWorkflowConfig.states.filter(sc => sc.name == w.state)[0]
      if (!stateConfig) {
        return null
      }
      var fieldPermissions = {}
      for (const f of this.dashboardFields) {
        fieldPermissions[f.name] = {'View': false}
      }
      for (const permission of stateConfig.permissions) {
        if (permission.action != 'View') {
          continue
        }
        if (this.userIsActor(w, permission)) {
          for (const af of permission.actionFields) {
            if (af == 'All') {
              for (const f of this.dashboardFields) {
                fieldPermissions[f.name][permission.action] = true
              }
              return fieldPermissions
            } else {
              if (fieldPermissions[af] != undefined) {
                fieldPermissions[af][permission.action] = true
              }
            }
          }
        }
      }
      return fieldPermissions
    },
    userIsActor (workflow, permission) {
      var allowedGroups = permission.groups
      for (const g of allowedGroups) {
        if (this.orgUser.groups.includes(g)) {
          return true
        }
      }
      var others = permission.others
      for (const o of others) {
        if (o == 'Workflow Creator') {
          if (workflow.createdBy == this.email) {
            return true
          }
        } else {
          var field = null
          for (const f of this.orgWorkflowConfig.fields) {
            if (f.name == o) {
              field = f
            }
          }
          if (field) {
            if (field.type == 'string') {
              if (this.email == workflow[field.name]) {
                return true
              }
            }
            if (field.type == 'strings') {
              if (workflow[field.name].includes(this.email)) {
                return true
              }
            }
          }
        }
      }
      return false
    },
    getFolders () {
      this.$http.get(this.server + '/org/get-folders-for-workflow-config/' + this.configId + '/').then(resp => {
        this.$store.commit('folders/setFolderMap', resp.body)
      }, err => {
        console.log('Failed to get folders')
      })
    },
    openFolderModal (folder) {
      var canDelete = false
      if (folder && !this.subfolders.length && !this.workflows.length) {
        canDelete = true
      }
      this.folderModal = {
        opened: true,
        folder: folder,
        canDelete: canDelete,
      }
    },
    openMoveWorkflowModal () {
      this.moveWorkflowModal = {
        opened: true
      }
    },
    closeMoveWorkflowModal (moved) {
      if (moved) {
        this.getWorkflowsInFolder()
      }
      this.$store.commit('folders/selectFolder', null)
      this.moveWorkflowModal.opened = false
    },
    openExportWorkflowModal (selected) {
      if (selected) {
        if (this.selectedWorkflows.length) {
          this.exportWorkflowModal = {
            workflows: this.selectedWorkflows,
            opened: true,
          }
        }
      } else {
        if (this.workflows.length) {
          this.exportWorkflowModal = {
            workflows: this.workflows,
            opened: true,
          }
        }
      }
    },
    closeExportWorkflowModal () {
      this.exportWorkflowModal.opened = false
    },
  },
  mounted () {
    this.getWorkflowsInFolder()
    if (!this.folderMap) {
      this.getFolders()
    }
    this.localFilter = this.workflowFilter
  },
}
</script>

<style scoped lang="scss">
.my-folder-name {
  position: relative;
  top: 5px;
}
</style>
