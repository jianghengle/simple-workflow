<template>
  <div>
    <nav class="breadcrumb" aria-label="breadcrumbs">
      <ul>
        <li v-for="(p, i) in paths" :key="'address-bar-path-' + i">
          <router-link href="#" aria-current="page" :to="p.path">{{p.name}}</router-link>
        </li>
        <li class="is-active"><a href="#" aria-current="page">{{currentName}}</a></li>
      </ul>
    </nav>
  </div>
</template>

<script>

export default {
  name: 'AddressBar',
  props: ['workflowFolderId'],
  data () {
    return {
      localModel: null,
    }
  },
  computed: {
    orgId () {
      return this.$route.params.orgId
    },
    configId () {
      return this.$route.params.configId
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
    folderId () {
      return this.$route.params.folderId
    },
    folderMap () {
      return this.$store.state.folders.folderMap
    },
    folder () {
      if (this.folderMap && this.folderId) {
        return this.folderMap[this.folderId]
      }
    },
    workflowId () {
      return this.$route.params.workflowId
    },
    currentName () {
      if (this.workflowId) {
        return this.workflowId
      }
      if (this.folderId == this.configId) {
        return this.orgWorkflowConfig && this.orgWorkflowConfig.name
      }
      return this.folder && this.folder.name
    },
    paths () {
      var paths = []
      if (!this.folderMap) {
        return paths
      }
      var parentId = this.folder ? this.folder.parentId : this.workflowFolderId
      while (parentId) {
        var parentFolder = this.folderMap[parentId]
        paths.unshift({
          name: parentFolder.parentId ? parentFolder.name : this.orgWorkflowConfig.name,
          path: '/org/' + this.orgId + '/workflow-folder/' + this.configId + '/' + parentFolder.id,
        })
        parentId = parentFolder.parentId
      }
      return paths
    },
  },
}
</script>

<style scoped lang="scss">

</style>
