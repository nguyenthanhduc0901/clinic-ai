import requests
import json


API = "http://127.0.0.1:8000/v1/text/analyze"


if __name__ == "__main__":
    dialogue = (
        "dạ chào bác sĩ em… em dạo này thấy người mệt lắm, chắc cũng hơn một tháng nay rồi đó, cứ tới chiều chiều tối tối là lại hay bị sốt nhẹ nhẹ, nó không cao lắm đâu, kiểu âm ỉ thôi chứ không có dữ dội. ban ngày thì cũng mệt, nhưng mà tới chiều thì em thấy rõ ràng hơn, nó cứ uể oải làm sao. à… sáng ra lúc mới ngủ dậy thì mấy cái khớp ở ngón tay nó bị cứng, em phải ngồi một hồi, chắc tầm hai mươi ba mươi phút gì đó thì mới cử động bình thường được. em còn để ý trên mặt có cái ban đỏ ở hai bên má, nhìn gương thì thấy, mà đặc biệt là đi ngoài nắng thì nó đỏ rõ lắm. với lại dạo này em cứ hay bị nhiệt miệng, nó hết rồi lại bị lại, rồi tóc thì rụng nhiều lắm, mỗi lần chải hay gội là rơi cả nắm, em lo quá không biết có sao không…"
    )

    r = requests.post(API, json={"text": dialogue}, timeout=600)
    r.raise_for_status()
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))


