from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
from django.utils import timezone
from .models import GameRecord, Movie
import json
from rest_framework.response import Response

# .env 파일 로드
load_dotenv()
# API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_movie_context(movie_id):
    #movie = Movie.objects.get(id=movie_id)
    movie = Movie.objects.get(id=movie_id) # 일단 1로..
    return movie.context


# OpenAI 모델 초기화
chat = ChatOpenAI(temperature=0.5, openai_api_key=OPENAI_API_KEY)


game_record = [  # 각 라운드의 기록
    
]

# 프롬프트 템플릿 정의
# 프롬프트를 잘 만지자. 답변 형식도 지정해줘야 할 듯.
evaluation_prompt = PromptTemplate(
    input_variables=["situation", "user_action", "context"],
    template=(
        "상황: {situation}\n"
        "세계관 정보: {context}\n"
        "유저의 행동: {user_action}\n\n"
        "질문:\n"
        "1. 유저의 행동을 0~100 점으로 평가하고, 50점을 기준으로 True 또는 False로 적절성을 판단하세요.\n"
        "2. 판단의 이유를 설명하세요.\n"
        "3. 이 상황에서 이어지는 새로운 문제 상황을 작성하세요. 새로운 문제 상황은 해리포터 세계관에 맞게 작성하고, "
        "유저가 해결해야 할 도전 과제를 포함해야 합니다."
    )
)

# 게임 진행 요약을 위한 프롬프트
summary_prompt = PromptTemplate(
    input_variables = ["history"],
    template = (
        "다음은 유저와의 대화 기록입니다:\n"
        "{history}\n\n"
        "이 기록을 기반으로 전체 이야기를 요약하세요. 요약은 한 편의 영화 줄거리처럼 작성되어야 하며, "
        "유저가 해결한 문제와 그 행동, 그리고 상황의 흐름을 포함해야 합니다. "
    )
)


# 행동 평가 및 다음 상황 생성 함수
def evaluate_and_generate_next(situation, user_action,context):
    """
    사용자 행동을 평가하고 다음 상황을 생성하는 함수
    """
    llm_chain = LLMChain(llm=chat, prompt=evaluation_prompt)
    result = llm_chain.run({
        "situation": situation,
        "user_action": user_action,
        "context" : context,
    })
    return result

# 평가 결과 처리
def process_evaluation_and_next(result):
    """
    AI의 응답을 분석하여 점수, 유효성, 이유, 다음 문제를 추출하는 함수
    """
    lines = result.split("\n")
    try:
        # 점수를 포함한 텍스트에서 숫자만 추출
        score_text = lines[0].split("점")[0].split()[-1].strip()
        score = int(score_text)  # 정수로 변환
        is_valid = score >=50
    except (ValueError, IndexError):
        score = 0  # 오류 발생 시 기본값 설정
    
    is_valid = "True" in lines[0]
    reason = lines[1].replace("2. ", "").strip()
    next_problem = lines[2].replace("3. 새로운 문제 상황: ", "").strip()
    
    return score, is_valid, reason, next_problem


# 게임 요약 생성
def generate_summary(history):
    """
    게임 진행 기록을 바탕으로 전체 스토리 요약을 생성하는 함수
    """
    llm_chain = LLMChain(llm=chat, prompt=summary_prompt)
    result = llm_chain.run({
        "history":history
    })
    return result



def play_game_round(game_record, user_action):
    # history가 문자열일 경우 JSON으로 변환
    if isinstance(game_record.history, str):
        try:
            history = json.loads(game_record.history) or []
        except json.JSONDecodeError:
            history = []
    else:
        history = game_record.history or []

    # 현재 라운드 확인
    current_round = len(history) + 1

    # 현재 상황 가져오기
    if history:
        current_situation = history[-1]['next_situation']
    else:
        # 초기 질문 설정
        initial_question = game_record.movie.initial_questions.order_by('?').first()
        if not initial_question:
            return Response({"error": "No initial questions available for this movie."}, status=400)
        current_situation = initial_question.question

    # 행동 평가 및 다음 상황 생성
    evaluation_result = evaluate_and_generate_next(
        situation=current_situation,
        user_action=user_action,
        context=get_movie_context(game_record.movie.id),
    )

    # 응답 처리
    score, is_valid, reason, next_problem = process_evaluation_and_next(evaluation_result)

    # 새로운 라운드 데이터 추가
    round_data = {
        "round": current_round,
        "situation": current_situation,
        "user_action": user_action,
        "score": score,
        "evaluation": "적절함" if is_valid else "부적절함",
        "reason": reason,
        "next_situation": next_problem
    }

    # 중복 방지: 현재 라운드가 이미 존재하는지 확인
    if not any(entry['round'] == current_round for entry in history):
        history.append(round_data)

    # 기록 업데이트
    game_record.history = json.dumps(history, ensure_ascii=False)  # 직렬화하여 JSON으로 저장
    game_record.total_score += score

    # 게임 종료 조건 확인
    is_game_over = len(history) >= 5
    if is_game_over:
        game_record.end_time = timezone.now()
        game_record.end_status = 'COMPLETED'

    game_record.save()
    print('game_record 저장')

    return next_problem, is_game_over, reason, is_valid

def play_game_round2(game_record, user_action):
    # history 초기화
    if isinstance(game_record.history, str):
        try:
            history = json.loads(game_record.history) or []
        except json.JSONDecodeError:
            history = []
    else:
        history = game_record.history or []

    # 현재 라운드 계산
    # current_round = len(history) + 1
    if not history:
        current_round = 0  # 첫 라운드일 경우 0으로 설정
    else :
        current_round +=1

    # 현재 상황 가져오기
    if history:
        current_situation = history[-1]['next_situation']
    else:
        # 초기 질문 설정
        initial_question = game_record.movie.initial_questions.order_by('?').first()
        if not initial_question:
            return Response({"error": "No initial questions available for this movie."}, status=400)

        # 첫 라운드 생성
        current_situation = initial_question.question
        round_data = {
            "round": 1,
            "situation": current_situation,
            "user_action": None,
            "score": 0,
            "evaluation": None,
            "reason": None,
            "next_situation": None
        }
        history.append(round_data)

    # 행동 평가 및 다음 상황 생성
    evaluation_result = evaluate_and_generate_next(
        situation=current_situation,
        user_action=user_action,
        context=get_movie_context(game_record.movie.id),
    )

    # 응답 처리
    score, is_valid, reason, next_problem = process_evaluation_and_next(evaluation_result)

    # 라운드 데이터 생성
    round_data = {
        "round": current_round,
        "situation": current_situation,
        "user_action": user_action,
        "score": score,
        "evaluation": "적절함" if is_valid else "부적절함",
        "reason": reason,
        "next_situation": next_problem
    }

    # 중복 방지 및 추가
    if history and any(entry['round'] == current_round for entry in history):
        print(f"Round {current_round} already exists in history.")
    else:
        history.append(round_data)

    # 기록 업데이트
    game_record.history = json.dumps(history, ensure_ascii=False)
    game_record.total_score += score

    # 게임 종료 조건 확인
    is_game_over = len(history) >= 5
    if is_game_over:
        game_record.end_time = timezone.now()
        game_record.end_status = 'COMPLETED'

    game_record.save()

    # 디버깅 로그 추가
    print(f"Current Round: {current_round}")
    print(f"History Length: {len(history)}")
    print(f"History Data: {history}")
    print(f"Next Problem: {next_problem}")
    print(f"Is Game Over: {is_game_over}")

    return next_problem, is_game_over, reason, is_valid

    # history 초기화
    if isinstance(game_record.history, str):
        try:
            history = json.loads(game_record.history) or []
        except json.JSONDecodeError:
            history = []
    else:
        history = game_record.history or []

    # 현재 라운드 계산
    current_round = len(history) + 1

    # 현재 상황 가져오기
    if history:
        current_situation = history[-1]['next_situation']
    else:
        # 초기 질문 설정
        initial_question = game_record.movie.initial_questions.order_by('?').first()
        if not initial_question:
            return Response({"error": "No initial questions available for this movie."}, status=400)

        # 첫 라운드 생성
        current_situation = initial_question.question
        first_round_data = {
            "round": current_round,
            "situation": current_situation,
            "user_action": None,
            "score": 0,
            "evaluation": None,
            "reason": None,
            "next_situation": None
        }
        history.append(first_round_data)

    # 행동 평가 및 다음 상황 생성
    evaluation_result = evaluate_and_generate_next(
        situation=current_situation,
        user_action=user_action,
        context=get_movie_context(game_record.movie.id),
    )

    # 응답 처리

def play_game_round4(game_record, user_action):
    # history 초기화
    if isinstance(game_record.history, str):
        try:
            history = json.loads(game_record.history) or []
        except json.JSONDecodeError:
            history = []
    else:
        history = game_record.history or []

    # 현재 라운드 계산
    current_round = len(history) + 1

    # 현재 상황 가져오기
    if history:
        current_situation = history[-1]['next_situation']
    else:
        # 초기 질문 설정
        initial_question = game_record.movie.initial_questions.order_by('?').first()
        if not initial_question:
            return None, None, "No initial questions available for this movie.", False  # 기본 반환값
        # 첫 라운드 데이터 추가
        current_situation = initial_question.question
        first_round_data = {
            "round": current_round,
            "situation": current_situation,
            "user_action": None,
            "score": 0,
            "evaluation": None,
            "reason": None,
            "next_situation": None
        }
        history.append(first_round_data)

    # 행동 평가 및 다음 상황 생성
    try:
        evaluation_result = evaluate_and_generate_next(
            situation=current_situation,
            user_action=user_action,
            context=get_movie_context(game_record.movie.id),
        )
        # 응답 처리
        score, is_valid, reason, next_problem = process_evaluation_and_next(evaluation_result)
    except Exception as e:
        return None, None, str(e), False  # 예외 발생 시 기본 반환값

    # 새로운 라운드 데이터 추가
    round_data = {
        "round": current_round,
        "situation": current_situation,
        "user_action": user_action,
        "score": score,
        "evaluation": "적절함" if is_valid else "부적절함",
        "reason": reason,
        "next_situation": next_problem
    }
    history.append(round_data)

    # 기록 업데이트
    game_record.history = json.dumps(history, ensure_ascii=False)
    game_record.total_score += score

    # 게임 종료 조건 확인
    is_game_over = len(history) >= 5
    if is_game_over:
        game_record.end_time = timezone.now()
        game_record.end_status = 'COMPLETED'

    game_record.save()

    # 디버깅 로그 추가
    print(f"Current Round: {current_round}")
    print(f"History Length: {len(history)}")
    print(f"History Data: {history}")
    print(f"Next Problem: {next_problem}")
    print(f"Is Game Over: {is_game_over}")

    # 모든 조건에서 반환
    return next_problem, is_game_over, reason, is_valid

def generate_game_summary(game_record):
    history = json.loads(game_record.history) if isinstance(game_record.history, str) else game_record.history
    
    formatted_history = "\n".join(
        f"라운드 {entry.get('round', 'N/A')}: [상황]: {entry.get('situation', 'N/A')}\n"
        f" [행동]: {entry.get('user_action', 'N/A')}\n"
        f" [평가]: {entry.get('evaluation', 'N/A')}, 점수: {entry.get('score', 0)}"
        for entry in history
    )
    
    summary = generate_summary(formatted_history)
    return summary