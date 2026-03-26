<template>
  <div class="exquis-app">
    <header class="header">
      <div class="logo">
        <span class="logo-icon">🧠</span>
        <h1>Exquis</h1>
      </div>
      <div class="status">
        <span :class="['status-dot', apiConnected ? 'connected' : 'disconnected']"></span>
        {{ apiConnected ? 'API Connected' : 'Connecting...' }}
      </div>
    </header>

    <main class="main-content">
      <div class="upload-section">
        <div class="upload-area" 
             @dragover.prevent 
             @drop.prevent="handleDrop"
             @click="triggerFileInput">
          <div v-if="!previewImage" class="upload-placeholder">
            <span class="upload-icon">📷</span>
            <p>Drop an image here or click to upload</p>
            <p class="subtext">Supports JPG, PNG, WebP</p>
          </div>
          <img v-else :src="previewImage" class="preview-image" />
        </div>
        <input 
          ref="fileInput"
          type="file" 
          accept="image/*" 
          @change="handleFileSelect" 
          style="display: none;"
        />
        
        <div class="controls">
          <div class="population-control">
            <label>Population Size:</label>
            <input 
              type="range" 
              v-model="populationSize" 
              min="10" 
              max="1000" 
              step="10"
            />
            <span>{{ populationSize }}</span>
          </div>
          
          <button 
            class="analyze-btn" 
            @click="analyzeImage"
            :disabled="!previewImage || isAnalyzing"
          >
            {{ isAnalyzing ? 'Analyzing...' : 'Analyze Brain Response' }}
          </button>
        </div>
      </div>

      <div v-if="currentCaption" class="caption-section">
        <h3>Image Caption</h3>
        <p>{{ currentCaption }}</p>
      </div>

      <div v-if="populationData" class="results-section">
        <div class="section-header">
          <h2>Brain Response Analysis</h2>
          <div class="population-info">
            {{ populationData.population_size }} brains analyzed
          </div>
        </div>

        <div class="visualization-grid">
          <div class="brain-map-card card">
            <h3>Brain Activation Map</h3>
            <div class="brain-regions">
              <div 
                v-for="(data, region) in populationData.visualization" 
                :key="region"
                class="region-bar"
              >
                <span class="region-name">{{ region }}</span>
                <div class="bar-container">
                  <div 
                    class="bar-fill" 
                    :style="{ width: (data.mean * 100) + '%' }"
                  ></div>
                </div>
                <span class="region-value">{{ (data.mean * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <div class="distribution-card card">
            <h3>Activation Distribution</h3>
            <div class="distribution-histogram">
              <div 
                v-for="(data, region) in populationData.visualization" 
                :key="region"
                class="dist-row"
              >
                <span class="dist-label">{{ region }}</span>
                <div class="dist-bars">
                  <div 
                    v-for="(count, idx) in data.histogram.counts" 
                    :key="idx"
                    class="hist-bar"
                    :style="{ 
                      height: (count / Math.max(...data.histogram.counts) * 40) + 'px',
                      backgroundColor: getBarColor(data.mean)
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="simulation-section">
          <div class="simulation-header">
            <h3>Social Simulation</h3>
            <div class="mode-selector">
              <button 
                v-for="mode in ['posts', 'debate', 'consensus', 'all']" 
                :key="mode"
                :class="['mode-btn', { active: simulationMode === mode }]"
                @click="simulationMode = mode"
              >
                {{ mode }}
              </button>
            </div>
          </div>
          
          <button 
            class="run-simulation-btn"
            @click="runSimulation"
            :disabled="isSimulating"
          >
            {{ isSimulating ? 'Running Simulation...' : 'Run Social Simulation' }}
          </button>

          <div v-if="simulationResults" class="simulation-results">
            <div v-for="(modeResults, modeName) in simulationResults" :key="modeName" class="mode-results">
              <h4>{{ modeName }}</h4>
              
              <div v-if="modeResults.posts" class="posts-results">
                <div class="sentiment-bars">
                  <div class="sentiment-bar positive" :style="{ width: modeResults.posts.sentiment?.positive + '%' }"></div>
                  <div class="sentiment-bar neutral" :style="{ width: modeResults.posts.sentiment?.neutral + '%' }"></div>
                  <div class="sentiment-bar negative" :style="{ width: modeResults.posts.sentiment?.negative + '%' }"></div>
                </div>
                <div class="sentiment-labels">
                  <span>Positive: {{ modeResults.posts.sentiment?.positive?.toFixed(1) }}%</span>
                  <span>Neutral: {{ modeResults.posts.sentiment?.neutral?.toFixed(1) }}%</span>
                  <span>Negative: {{ modeResults.posts.sentiment?.negative?.toFixed(1) }}%</span>
                </div>
                
                <div class="sample-posts">
                  <div v-for="(post, idx) in modeResults.posts.posts?.slice(0, 5)" :key="idx" class="post-item">
                    <span class="agent-id">{{ post.agent_id }}</span>
                    <p>{{ post.reaction }}</p>
                  </div>
                </div>
              </div>
              
              <div v-if="modeResults.debates" class="debates-results">
                <p>Generated {{ modeResults.debates.total_debates }} debates</p>
              </div>
              
              <div v-if="modeResults.evolution" class="consensus-results">
                <p>Evolution over {{ modeResults.rounds }} rounds</p>
                <div v-for="(round, idx) in modeResults.evolution" :key="idx" class="round-result">
                  <span>Round {{ idx }}:</span>
                  <span>Pos: {{ round.sentiment?.positive?.toFixed(1) }}%</span>
                  <span>Neg: {{ round.sentiment?.negative?.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="agents-section">
          <h3>Sample Agents</h3>
          <div class="agents-grid">
            <div v-for="agent in sampleAgents" :key="agent.id" class="agent-card">
              <div class="agent-id">{{ agent.id }}</div>
              <div class="agent-regions">
                <span v-for="region in agent.dominant_regions" :key="region" class="region-tag">
                  {{ region }}
                </span>
              </div>
              <div class="agent-type">{{ agent.personality_type }}</div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default {
  name: 'App',
  setup() {
    const fileInput = ref(null)
    const previewImage = ref(null)
    const imageBase64 = ref(null)
    const populationSize = ref(10)
    
    const isAnalyzing = ref(false)
    const isSimulating = ref(false)
    const apiConnected = ref(false)
    
    const currentCaption = ref(null)
    const populationData = ref(null)
    const simulationResults = ref(null)
    
    const simulationMode = ref('posts')
    const sampleAgents = ref([])

    const checkApiHealth = async () => {
      try {
        const res = await axios.get(`${API_URL}/health`)
        apiConnected.value = res.data.status === 'healthy'
      } catch {
        apiConnected.value = false
      }
    }

    const triggerFileInput = () => {
      fileInput.value.click()
    }

    const handleFileSelect = (e) => {
      const file = e.target.files[0]
      if (file) {
        processFile(file)
      }
    }

    const handleDrop = (e) => {
      const file = e.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        processFile(file)
      }
    }

    const processFile = (file) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        previewImage.value = e.target.result
        imageBase64.value = e.target.result.split(',')[1]
      }
      reader.readAsDataURL(file)
    }

    const analyzeImage = async () => {
      if (!imageBase64.value) return
      
      isAnalyzing.value = true
      populationData.value = null
      simulationResults.value = null
      
      try {
        const res = await axios.post(`${API_URL}/image/analyze`, {
          image: imageBase64.value,
          population_size: populationSize.value
        })
        
        currentCaption.value = res.data.caption
        
        // Get visualization data
        const vizRes = await axios.get(`${API_URL}/brain/visualization`)
        populationData.value = vizRes.data
        
        // Get sample agents
        const agentsRes = await axios.get(`${API_URL}/agents/list`, {
          params: { limit: 6 }
        })
        sampleAgents.value = agentsRes.data.agents
        
      } catch (err) {
        console.error('Analysis failed:', err)
        alert('Analysis failed: ' + (err.response?.data?.error || err.message))
      } finally {
        isAnalyzing.value = false
      }
    }

    const runSimulation = async () => {
      if (!populationData.value) return
      
      isSimulating.value = true
      
      try {
        const res = await axios.post(`${API_URL}/simulation/run`, {
          mode: simulationMode.value
        })
        simulationResults.value = res.data.results
      } catch (err) {
        console.error('Simulation failed:', err)
        alert('Simulation failed: ' + (err.response?.data?.error || err.message))
      } finally {
        isSimulating.value = false
      }
    }

    const getBarColor = (mean) => {
      if (mean > 0.7) return '#ff6b6b'
      if (mean > 0.4) return '#ffd93d'
      return '#6bcb77'
    }

    onMounted(() => {
      checkApiHealth()
      setInterval(checkApiHealth, 10000)
    })

    return {
      fileInput,
      previewImage,
      populationSize,
      isAnalyzing,
      isSimulating,
      apiConnected,
      currentCaption,
      populationData,
      simulationResults,
      simulationMode,
      sampleAgents,
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      analyzeImage,
      runSimulation,
      getBarColor
    }
  }
}
</script>

<style>
.exquis-app {
  min-height: 100vh;
  background: #0f0f13;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #1a1a23;
  border-bottom: 1px solid #2a2a3a;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #888;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.connected {
  background: #6bcb77;
}

.status-dot.disconnected {
  background: #ff6b6b;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-area {
  border: 2px dashed #3a3a4a;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #15151f;
}

.upload-area:hover {
  border-color: #667eea;
  background: #1a1a28;
}

.upload-placeholder {
  color: #888;
}

.upload-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.subtext {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.5rem;
}

.preview-image {
  max-height: 300px;
  border-radius: 8px;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  align-items: center;
}

.population-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.population-control label {
  color: #888;
}

.population-control input[type="range"] {
  width: 200px;
}

.analyze-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.caption-section {
  background: #15151f;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.caption-section h3 {
  color: #667eea;
  margin-bottom: 0.5rem;
}

.results-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.population-info {
  color: #888;
}

.visualization-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card {
  background: #15151f;
  padding: 1.5rem;
  border-radius: 8px;
}

.card h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

.brain-regions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.region-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.region-name {
  width: 80px;
  font-size: 0.875rem;
  color: #aaa;
}

.bar-container {
  flex: 1;
  height: 8px;
  background: #2a2a3a;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.5s;
}

.region-value {
  width: 50px;
  text-align: right;
  font-size: 0.875rem;
  color: #888;
}

.distribution-histogram {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dist-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dist-label {
  width: 80px;
  font-size: 0.75rem;
  color: #888;
}

.dist-bars {
  display: flex;
  gap: 2px;
  height: 40px;
  align-items: flex-end;
}

.hist-bar {
  width: 8px;
  border-radius: 2px;
}

.simulation-section {
  background: #15151f;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.simulation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.simulation-header h3 {
  color: #667eea;
}

.mode-selector {
  display: flex;
  gap: 0.5rem;
}

.mode-btn {
  padding: 0.5rem 1rem;
  background: #2a2a3a;
  border: none;
  border-radius: 6px;
  color: #888;
  cursor: pointer;
  text-transform: capitalize;
}

.mode-btn.active {
  background: #667eea;
  color: white;
}

.run-simulation-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 1rem;
}

.run-simulation-btn:disabled {
  opacity: 0.5;
}

.simulation-results {
  margin-top: 1rem;
}

.mode-results {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #1a1a23;
  border-radius: 6px;
}

.mode-results h4 {
  color: #667eea;
  margin-bottom: 0.5rem;
  text-transform: capitalize;
}

.sentiment-bars {
  display: flex;
  height: 20px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.sentiment-bar {
  transition: width 0.5s;
}

.sentiment-bar.positive {
  background: #6bcb77;
}

.sentiment-bar.neutral {
  background: #ffd93d;
}

.sentiment-bar.negative {
  background: #ff6b6b;
}

.sentiment-labels {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: #888;
}

.sample-posts {
  margin-top: 1rem;
}

.post-item {
  padding: 0.75rem;
  background: #15151f;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.agent-id {
  font-size: 0.75rem;
  color: #667eea;
  display: block;
  margin-bottom: 0.25rem;
}

.post-item p {
  font-size: 0.875rem;
  color: #ccc;
}

.agents-section {
  background: #15151f;
  padding: 1.5rem;
  border-radius: 8px;
}

.agents-section h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.agent-card {
  padding: 1rem;
  background: #1a1a23;
  border-radius: 6px;
  text-align: center;
}

.agent-id {
  font-size: 0.875rem;
  color: #667eea;
  display: block;
  margin-bottom: 0.5rem;
}

.agent-regions {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.region-tag {
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  background: #2a2a3a;
  border-radius: 4px;
  color: #aaa;
}

.agent-type {
  font-size: 0.75rem;
  color: #888;
  text-transform: capitalize;
}
</style>