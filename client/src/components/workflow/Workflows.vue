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

      <nav class="breadcrumb" aria-label="breadcrumbs">
        <ul>
          <li class="is-active"><a href="#" aria-current="page">{{orgWorkflowConfig.name}}</a></li>
        </ul>
      </nav>

      <div>  
        <div class="buttons is-pulled-right">
          <router-link :to="'/org/' + orgId + '/new-workflow/' + this.configId + '/' + this.folderId + '/new'" class="button">
            <span class="icon">
              <i class="fas fa-plus"></i>
            </span>
            <span>New Workflow</span>
          </router-link>
        </div>
        <h1 class="title is-4">{{orgWorkflowConfig.name}}</h1>
        <h2 class="subtitle is-6">&nbsp;</h2>
      </div>
  
      <div v-if="workflows">
        
        <div class="columns mt-4">
          <div class="column field mb-0 pb-0">
            <p class="control has-icons-left">
              <span class="select">
                <select v-model="filter">
                  <option :value="'CurrentFolder'">All</option>
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
                <th>
                  <input type="checkbox">
                </th>
                <th class="is-clickable" @click="changeSortOption('id')">
                  <span>Id</span>
                  <span class="icon" v-if="sortOption.field == 'id'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
                <th class="has-text-centered is-clickable" @click="changeSortOption('state')">
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
                <th class="is-clickable" @click="changeSortOption('updatedAt')">
                  <span>Updated At</span>
                  <span class="icon" v-if="sortOption.field == 'updatedAt'">
                    <i class="fas" :class="{'fa-sort-up': sortOption.asc, 'fa-sort-down': !sortOption.asc}"></i>
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr class="is-clickable" v-for="(w, i) in showingWorkflows" :key="'wftbr-' + i" @click="viewWorkflow(w)">
                <td><input type="checkbox"></td>
                <td>{{w.id}}</td>
                <td class="has-text-centered">
                  <span class="tag is-link" :style="{'background-color': w.stateColor}">{{w.state}}</span>
                </td>
                <td v-for="(f, j) in dashboardFields" :key="'wftb-r-' + i + '-c-' + j" :class="{'has-text-right': f.type=='number'}">
                  {{w[f.name]}}
                </td>
                <td>{{w.createdBy}}</td>
                <td>{{w.createdAtLabel}}</td>
                <td>{{w.updatedAtLabel}}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else>
          <article class="message is-info">
            <div class="message-body">
              No workflow found.
            </div>
          </article>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import dateFormat from 'dateformat'

export default {
  name: 'Workflows',
  data () {
    return {
      error: '',
      waiting: false,
      folder: null,
      workflows: null,
      filter: 'CurrentFolder',
      search: '',
      sortOption: {
        field: 'createdAt',
        asc: true
      }
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
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
      return this.orgUser.role == 'Owner' || this.orgUser.role == 'Admin'
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
      return this.orgWorkflowConfig.fields.filter(f => f.dashboard)
    },
    parentFolders () {
      return []
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
      var filteredWorkflows = mappedWorkflows.filter(w => {
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
      var sortedWorkflows = filteredWorkflows.sort((a, b) => {
        var va = a[sort.field]
        var vb = b[sort.field]
        if (sort.field == 'createdAt') {
          return sort.asc ? va - vb : vb - va
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
  },
  watch: {
    folderId: function (val) {
      this.getWorkflowsInFolder()
    },
  },
  methods: {
    getWorkflowsInFolder () {
      this.waiting = true
      this.$http.get(this.server + '/org/get-org-workflows-in-folder/' + this.folderId).then(resp => {
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
      for (var w of workflows) {
        var fieldPermissions = this.getFieldPermissions(w)
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
        }
      }
      return processed
    },
    getFieldPermissions (w) {
      var stateConfig = this.orgWorkflowConfig.states.filter(sc => sc.name == w.state)[0]
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
  },
  mounted () {
    this.getWorkflowsInFolder()
  },
}
</script>

<style scoped lang="scss">
.workflow-id {
  max-width: 60px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
