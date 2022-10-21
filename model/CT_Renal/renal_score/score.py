# 肾肿瘤评分
class Renal():
    def __init__(self):
        self.R = ["<4cm", "4~7cm", ">7cm"]  # 半径 Radius (maximal diameter in cm)
        self.E = [">50%", "<50%", "0"]  # 内生性 Exophytic/endophytic properties
        self.N = [">7mm", "4~7mm", "<4mm"]  # 距离肾门位置 Nearness of the tumor to the collecting system or sinus (mm)
        self.L = ["outer",  # 完全在上下极线之外
                  "through",  # 肿瘤穿过肾极线
                  "inner"]  # 与肾上下极的位置关系 Location relative to the polar lines
        # 只有前四项给分，分别是1~3分，最小4分 最大12分
        # 4~6为低度复杂性 7~9中度 10~12高度
        self.A = ["A", "P", "X"]  # 位于腹/背侧 Anterior/Posterior 不给分，只附加后缀A, P, X
        self.H = ["H"]  # 如果肿瘤触及主肾动脉或静脉，则指定后缀“H”
        # 给出评分如  9ah 4p 12xh

    def getscore(self, input):
        score = 0
        comp = ""
        if input.get("R") is not None:
            r = int(input.get("R"))
            if r <= 4:
                score += 1
            elif r <= 7:
                score += 2
            else:
                score += 3

        if input.get("E") is not None:
            e = int(input.get("E"))
            if e > 50:
                score += 1
            elif e > 0:
                score += 2
            else:
                score += 3

        if input.get("N") is not None:
            n = int(input.get("N"))
            if n >= 7:
                score += 1
            elif n >= 4:
                score += 2
            else:
                score += 3
        if input.get("L").lower() in self.L:
            l = self.L.index(input.get("L").lower()) + 1
            score += l
        if score <= 6:
            comp = "低度复杂性 "
        elif score <= 9:
            comp = "中度复杂性 "
        else:
            comp = "高度复杂性 "
        if input.get("A").upper() in self.A:
            score = str(score)
            score += input.get("A").lower()
        if input.get("H").upper() in self.H:
            score = str(score)
            score += input.get("H").lower()
        return comp, score


if __name__ == '__main__':
    inp = {"R": 3,
           "E": 50,
           "N": 1,
           "L": "INNER",
           "A": "X",
           "H": "H"
           }
    test = Renal()
    sc = test.getscore(inp)
    print(sc)
