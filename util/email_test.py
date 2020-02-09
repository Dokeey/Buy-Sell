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
                    result
                )



if __name__ == '__main__':
    cnt = None
    if len(sys.argv) > 1:
        cnt = int(sys.argv[1])

    l = Lotto(cnt)
    l.result()