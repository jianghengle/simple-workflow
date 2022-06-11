<template>
  <div>
    <div class="this-folder-name" :class="{'disabled-folder': sourceFolderId == folderId, 'this-folder-selected': selectedFolderId == folderId}" @click="selectFolder">
      <span class="icon-text">
        <span class="icon">
          <i class="fas fa-folder"></i>
        </span>
        <span>{{folderName}}</span> &nbsp;
        <span v-if="sourceFolderId == folderId">(Current folder)</span>
      </span>
    </div>
    <div v-if="subfolders.length" class="the-sub-folders">
      <folder-tree-node v-for="(f, i) in subfolders" :key="folderId + '-sub-' + i" :folderId="f.id" :sourceFolderId="sourceFolderId" />
    </div>
  </div>
</template>

<script>
import FolderTreeNode from './FolderTreeNode'

export default {
  name: 'folder-tree-node',
  components: {
    FolderTreeNode
  },
  props: ['folderId', 'sourceFolderId'],
  data () {
    return {
      waiting: false,
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
    folderMap () {
      return this.$store.state.folders.folderMap
    },
    folder () {
      if (!this.folderMap) {
        return null
      }
      return this.folderMap[this.folderId] 
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
    folderName () {
      if (!this.folder) {
        return ''
      }
      if (this.folderId == this.configId) {
        return this.orgWorkflowConfig.name
      }
      return this.folder.name
    },
    selectedFolderId () {
      return this.$store.state.folders.selectedFolderId
    },
  },
  methods: {
    selectFolder () {
      if (this.folderId != this.sourceFolderId) {
        this.$store.commit('folders/selectFolder', this.folderId)
      }
    },
  },
}
</script>

<style scoped>
.this-folder-name {
  border-radius: 2px;
  color: #4a4a4a;
  padding: 0.5em 0.75em;
  cursor: pointer;
}

.this-folder-name:hover {
  background-color: hsl(0, 0%, 96%);
}

.the-sub-folders {
  border-left: 1px solid #dbdbdb;
  margin-left: 0.75em;
  padding-left: 0.75em;
}

.disabled-folder {
  cursor: auto;
  -webkit-text-fill-color: #7a7a7a;
  color: #7a7a7a;
}

.this-folder-selected {
  background-color: #485fc7!important;
  color: #fff
}

</style>
