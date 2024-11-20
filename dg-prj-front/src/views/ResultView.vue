<template>
    <div>
        <h1>최종 결과 페이지</h1>
        <hr>
        <!-- <p style="font-size: small">{{ result.history }}</p> -->
        <!-- {{ result.history }} -->
        <div v-for="(res,index) in result.history">
            <p>{{ index }}번 라운드</p>
            <p>{{ res.situation }}</p>
            <hr>
        </div>
    </div>
</template>

<script setup>
import { useGameStore, useUserStore } from '@/stores/counter';
import axios from 'axios';
import { onMounted, ref } from 'vue';
const result = ref()
const gamestore = useGameStore()
const userstore= useUserStore()

onMounted(() => {
    console.log('gamenum:' ,gamestore.game_id)
    axios({
        method:'get',
        url:`http://127.0.0.1:8000/gameApp/movie/${gamestore.game_id}/`,
        headers : {
            Authorization: `Token ${userstore.token}`
        }
    })
    .then(res => {
        console.log(res.data); // 이러면 JSON 문자열 그대로 반환됨. 
            // history가 JSON 문자열인 경우 파싱
            if (typeof res.data.history === 'string') {
                res.data.history = JSON.parse(res.data.history); // 그래서 파싱 해줌.
            }
            result.value = res.data; 
})
    .catch(err=> console.log(err))
})

</script>

<style lang="scss" scoped>

</style>