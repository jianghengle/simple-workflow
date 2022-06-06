import Vue from 'vue'

// initial state
export const state = {
  folderMap: null,
}
 
 // mutations
export const mutations = {
  setFolderMap (state, folders) {
    var folderMap = {}
    for (const f of folders) {
      folderMap[f.id] = f
    }
    state.folderMap = folderMap
  },
  addFolder (state, folder) {
    Vue.set(state.folderMap, folder.id, folder)
  },
  updateFolder (state, folder) {
    state.folderMap[folder.id] = folder
  },
  removeFolder (state, folderId) {
    var folderMap = {}
    for (const id in state.folderMap) {
      if (id != folderId) {
        folderMap[id] = state.folderMap[id]
      }
    }
    state.folderMap = folderMap
  },
}
 
export default {
  namespaced: true,
  state,
  mutations
}
