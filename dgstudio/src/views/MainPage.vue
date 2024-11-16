<template>
    <div>
        <h1>Type to Ending</h1>
    </div>
    <div style="display: flex; justify-content: space-between;">
        <!-- 로그인 창 -->
        <div class="login-container">
            <form >
                <label for="id">ID</label><br>
                <input type="text"><br>
                <label for="pw">Password</label><br>
                <input type="password"><br>
                

            </form>                     
        </div>

        <div class="howtoplay-container" @click="">
            how to play
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
const id = ref(null)
const password = ref(null)

</script>

<style scoped>
.login-container {
    border: 1px gray solid;
    border-radius: 5%;
    width: 30%;
    text-align: left;
    padding-left: 10px;
    margin-top: 5%;
}
.howtoplay-container {
    border: 1px white solid;
    background-color: red;
    font-weight: 600;
    padding: 10px;
    height: fit-content;
    margin-top: 5%;

}

</style>