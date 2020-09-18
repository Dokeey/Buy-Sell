import math
from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from accounts.supporter import send_mail
from random import randrange



class Lotto:
    def __init__(self, cnt=None):
        self.cnt = cnt

    # 중복제거, 정렬
    def create(self):
        num_list = list(range(1,46))
        lottos = []

        while len(lottos) < 6:
            lottos.append(num_list.pop(randrange(len(num_list))))

        return sorted(lottos)


    def count(self):
        if not self.cnt:
            return self.create()
        return [self.create() for x in range(self.cnt)]


    def result(self):
        result = self.count()
        if self.cnt is None:
            print(result)
        else:
            [print("{}번째 로또번호! : {}".format(i+1, lotto)) for i, lotto in enumerate(result)]

        self.send_email(result)


    def send_email(self, result):
        send_mail(
                    '[TEST] 로또 번호 받아랏',
                    ['ehdgnv@naver.com'],
                    "로또번호 입니다! {}".format(result)
                )

def sherlockAndAnagrams(ins, nums):
    cnt = 0
    LIMIT_NUM = 2 * 10 ** 8
    for num in nums:
        if cnt > 0:
            cnt -= 1
            continue
        if num < 25:
            if ins != 1:
                ins = math.ceil(ins / 2)
                cnt = 10
        elif num > 60:
            if ins * 2 < LIMIT_NUM:
                ins = ins * 2

    return ins


def solution(N, relation):
    result = []
    for person in range(1, N + 1):
        friends = []
        sub_friends = []
        for rel in relation:
            if person in rel:
                if rel[0] == person:
                    friends.append(rel[1])
                else:
                    friends.append(rel[0])

        for fr in friends:
            for rel in relation:
                if not person in rel and fr in rel:
                    if rel[0] == fr:
                        sub_friends.append(rel[1])
                    else:
                        sub_friends.append(rel[0])

        print(friends, sub_friends)
        friends = friends + sub_friends

        result.append(len(set(friends)))

    return result

if __name__ == '__main__':
    cnt = None
    if len(sys.argv) > 1:
        cnt = int(sys.argv[1])

    l = Lotto(cnt)
    l.result()
    # ins = 13
    # nums = [40, 89, 79, 76, 66, 60 ,8, 90, 19, 39, 53, 30, 93]
    # print(sherlockAndAnagrams(ins, nums))

    # n = [[1,2],[2,3],[2,5],[2,6],[4,2],[3,1],[4,5], [6,7]]
    # print(solution(7,n))
