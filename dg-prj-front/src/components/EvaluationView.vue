<template>
  <div class="evaluation-container">
    <div v-if="!isComplete" class="loading-section">
      <div class="loading-animation">
        <div class="pulse-ring"></div>
        <i class="bi bi-robot"></i>
      </div>
      <h1 class="loading-title">AI가 당신의 시나리오를 평가하는 중입니다</h1>
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
    
    <div v-else class="complete-section">
      <div class="success-animation">
        <i class="bi bi-check-circle-fill"></i>
      </div>
      <h1 class="complete-title">평가가 끝났습니다!</h1>
      <button class="next-button" @click="gonextStage">
        <span>확인하기</span>
        <i class="bi bi-arrow-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue';
import { useGameStore, useMovieStore, useUserStore } from '@/stores/counter';
import axios from 'axios';
import { useAccountStore } from '@/stores/accountStore';

const isComplete = ref(false)
const moviestore = useMovieStore()
const userstore = useUserStore()
const router = useRouter()
const gamestore = useGameStore()
const accountstore = useAccountStore()
  
onMounted(() => {
  // 3초 후에 이동
  axios({
    method:'post',
    url:`http://127.0.0.1:8000/gameApp/play_game/${gamestore.game_id}/`,
    headers : {
      Authorization: `Token ${accountstore.token}`
    },
    data: {
      user_action : gamestore.user_action1,
    } // 선택된 영화 ID를 이 변수에 담아 전송}
  })
  .then(res => {
    console.log(res)
    isComplete.value = true
    gamestore.next_situation = res.data.next_problem
    console.log(res.data)
    console.log(gamestore.next_situation)
    router.push({
      name: 'roundresult',
      state: { result: res.data }, // 데이터 상태로 전달
  });



  })
  .catch(err => {
    console.log(err)
  })
  
})
</script>

<style scoped>
.evaluation-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  padding: 2rem;
}

/* 로딩 섹션 스타일 */
.loading-section {
  text-align: center;
}

.loading-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 2rem;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid #830213;
  animation: pulse 1.5s ease-out infinite;
}

.loading-animation i {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 3rem;
  color: #830213;
}

.loading-title {
  color: #ffffff;
  font-size: 2rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.loading-dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background-color: #830213;
  border-radius: 50%;
  animation: dots 1.4s infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

/* 완료 섹션 스타일 */
.complete-section {
  text-align: center;
}

.success-animation {
  font-size: 5rem;
  color: #830213;
  margin-bottom: 2rem;
  animation: scale-in 0.5s ease-out;
}

.complete-title {
  color: #ffffff;
  font-size: 2rem;
  margin-bottom: 2rem;
  animation: fade-in 0.5s ease-out 0.3s both;
}

.next-button {
  background: #830213;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin: 0 auto;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fade-in 0.5s ease-out 0.6s both;
}

.next-button:hover {
  background: #9f0217;
  transform: translateY(-2px);
}

/* 애니메이션 */
@keyframes pulse {
  0% {
    transform: scale(0.95);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
  100% {
    transform: scale(0.95);
    opacity: 0.8;
  }
}

@keyframes dots {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(0.7);
    opacity: 0.5;
  }
}

@keyframes scale-in {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>