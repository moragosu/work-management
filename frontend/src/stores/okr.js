import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useOkrStore = defineStore('okr', () => {
  const objectives = ref([])
  const loading = ref(false)

  async function fetchObjectives() {
    loading.value = true
    try {
      const { data } = await axios.get('/api/okrs')
      objectives.value = data
    } finally {
      loading.value = false
    }
  }

  async function createObjective(objective) {
    const { data } = await axios.post('/api/okrs', objective)
    objectives.value.push(data)
    return data
  }

  async function updateObjective(id, patch) {
    const { data } = await axios.put(`/api/okrs/${id}`, patch)
    const idx = objectives.value.findIndex(o => o.id === id)
    if (idx !== -1) objectives.value[idx] = data
    return data
  }

  async function deleteObjective(id) {
    await axios.delete(`/api/okrs/${id}`)
    objectives.value = objectives.value.filter(o => o.id !== id)
  }

  async function addKeyResult(objectiveId, keyResult) {
    const { data } = await axios.post(`/api/okrs/${objectiveId}/key-results`, keyResult)
    const idx = objectives.value.findIndex(o => o.id === objectiveId)
    if (idx !== -1) {
      objectives.value[idx].key_results.push(data)
    }
    return data
  }

  async function updateKeyResult(objectiveId, krId, patch) {
    const { data } = await axios.put(`/api/okrs/${objectiveId}/key-results/${krId}`, patch)
    const idx = objectives.value.findIndex(o => o.id === objectiveId)
    if (idx !== -1) {
      const krIdx = objectives.value[idx].key_results.findIndex(kr => kr.id === krId)
      if (krIdx !== -1) {
        objectives.value[idx].key_results[krIdx] = data
      }
    }
    return data
  }

  async function deleteKeyResult(objectiveId, krId) {
    await axios.delete(`/api/okrs/${objectiveId}/key-results/${krId}`)
    const idx = objectives.value.findIndex(o => o.id === objectiveId)
    if (idx !== -1) {
      objectives.value[idx].key_results = objectives.value[idx].key_results.filter(kr => kr.id !== krId)
    }
  }

  function calcProgress(objective) {
    const keyResults = objective.key_results || []
    if (keyResults.length === 0) return 0
    const total = keyResults.reduce((sum, kr) => sum + (kr.progress || 0), 0)
    return Math.round(total / keyResults.length)
  }

  return {
    objectives,
    loading,
    fetchObjectives,
    createObjective,
    updateObjective,
    deleteObjective,
    addKeyResult,
    updateKeyResult,
    deleteKeyResult,
    calcProgress
  }
})