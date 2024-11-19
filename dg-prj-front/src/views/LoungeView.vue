<template>
    <div>
        <h1>Type to Ending</h1>
        <div class="theater-code" style="margin-top: -30px;">Theater Code : 0000 </div>

    </div>
    <div class="grid-container">
        <div>
            <!-- <img class="poster" :src="store.movieId ? require('@/assets/selectimg.jpeg') : require('@/assets/defaultimg.jpeg')" alt=""><br> -->
            <img class="poster" src='@/assets/selectimg.jpeg'><br>
            <button class="select-movie" @click="gogoSelect">영화 선택</button>
        </div>
        
        <div>
            <div class="description">
                <p style="font-size: medium; padding: 5px;" v-if="moviestore.movieId">{{moviestore.description}}</p>
                <p style="font-size: medium;" v-else>영화 줄거리가 들어갈 공간입니다.</p>
            </div>
            <button class="start-game" @click="startGame"
                    :class="{ 'red-background': moviestore.movieId }">
        게임 시작
    </button>

        </div>
        <div>
            <div class="howtoplay-container" @click="testFunc">
                how to play
            </div>
            <div><h3>Cast Info</h3>
            <p>주인공 : player {{ store.userId }}</p>
            <p>조연1 : player X</p>
            <p>조연2 : player X</p>

            </div>

        </div>
    </div>
</template>

<script setup>
import { useMovieStore, useUserStore } from '@/stores/counter';
import { useRouter } from 'vue-router';
const router = useRouter()
const store = useUserStore()
const moviestore = useMovieStore()

const gogoSelect = function(){
    router.push({name:'SelectMovie'})
}

const startGame = function () {

    
}



</script>

<style scoped>
.theater-code {
    background-color: black;
    width: 30%;
    padding: 10px;
    margin: auto;
}
.grid-container {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap:10px
}
.howtoplay-container {
    border-radius: 10px;
    background-color: red;
    font-weight: 600;
    padding: 10px;
    height: fit-content;
    width: fit-content;
    margin-top: 5%;
    margin-left: 50%;
}
.poster{
    width: 70%;
    margin-top: 30px;
}
.select-movie{
    color: white;
    background-color: red;
    padding: 5px 10px;
    font-size: large;
}
.description{
    margin-top: 20px;
    background-color: black;
    height: 85%;
}
.red-background {
    background-color: red;
    color: white; /* 버튼 글씨 색을 흰색으로 변경 */
}
.start-game {
    padding: 10px 20px;
    font-size: large;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}
</style>