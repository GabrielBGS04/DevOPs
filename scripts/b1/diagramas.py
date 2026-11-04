"""Renderiza diagramas de arquitetura para o Word; fontes Mermaid ficam ao lado."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/arquitetura/diagramas'
FONT='C:/Windows/Fonts/arial.ttf'
BOLD='C:/Windows/Fonts/arialbd.ttf'

class Diagram:
    def __init__(self,title,height=760):
        self.im=Image.new('RGB',(1600,height),'white'); self.d=ImageDraw.Draw(self.im)
        self.d.text((45,24),title,font=ImageFont.truetype(BOLD,34),fill='#142b40')
        self.d.text((45,height-40),'B1 · Arquitetura implementada no laboratório local · fontes Mermaid versionadas',font=ImageFont.truetype(FONT,22),fill='#41556a')
    def node(self,x,y,w,h,label,kind='container'):
        color={'container':'#e4edf6','database':'#f3f0df','component':'#e9f2ec','person':'#edf0f3','boundary':'#fafafa'}[kind]
        self.d.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=color,outline='#36566d',width=3)
        font=ImageFont.truetype(BOLD if kind=='container' else FONT,28)
        lines=label.split('\n'); lineheight=35
        yy=y+(h-lineheight*len(lines))/2
        for text in lines:
            box=self.d.textbbox((0,0),text,font=font); ww=box[2]-box[0]
            self.d.text((x+(w-ww)/2,yy),text,font=font,fill='#142b40'); yy+=lineheight
    def arrow(self,points,label='',offset=(0,-32),dashed=False):
        self.d.line(points,fill='#36566d',width=3)
        a,b=points[-2:]; ang=math.atan2(b[1]-a[1],b[0]-a[0]); r=15
        self.d.polygon([b,(b[0]-r*math.cos(ang-.5),b[1]-r*math.sin(ang-.5)),(b[0]-r*math.cos(ang+.5),b[1]-r*math.sin(ang+.5))],fill='#36566d')
        if label:
            p=points[len(points)//2]; x=p[0]+offset[0]; y=p[1]+offset[1]
            font=ImageFont.truetype(FONT,23); box=self.d.textbbox((x,y),label,font=font)
            self.d.rectangle((box[0]-5,box[1]-3,box[2]+5,box[3]+3),fill='white')
            self.d.text((x,y),label,font=font,fill='#142b40')
    def save(self,name): self.im.save(OUT/f'{name}.png')

def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    c=Diagram('Desafio 1   C4 Container do Core',600)
    c.node(60,230,240,130,'Aluno e equipe','person'); c.node(520,175,540,240,'Core Spring Boot\nAluno · Curso · Ranking\nGamificação\n[um processo Java]'); c.node(1270,225,270,140,'Banco relacional\n[JPA]','database')
    c.arrow([(300,295),(520,295)],'HTTP JSON',(-175,-40));c.arrow([(1060,295),(1270,295)],'JPA',(-145,-40)); c.save('core')
    a=Diagram('Desafio 3   C4 Container com fronteira da IA',650)
    a.node(60,170,240,130,'Aluno','person');a.node(500,140,370,190,'Core Spring Boot\n:8080\nFallback explícito');a.node(1100,140,430,190,'IA FastAPI :8001\nRecomendação local\nAssistente demonstrativo');a.node(500,430,370,120,'Banco relacional','database')
    a.arrow([(300,235),(500,235)],'HTTP',(-150,-38));a.arrow([(870,235),(1100,235)],'HTTP / 2s',(-195,-38));a.arrow([(685,330),(685,430)],'JPA',(25,-60));a.save('ai')
    c=Diagram('Desafio 2   C4 Component do fluxo de conclusão',900)
    c.node(40,140,310,120,'AlunoController','component');c.node(440,140,310,120,'AlunoService\nTransação','component');c.node(840,140,310,120,'ConclusaoDeCurso','component');c.node(1240,140,310,120,'Aluno','component')
    c.node(840,410,310,120,'ConclusaoPort\n[interface]','component');c.node(1240,410,310,120,'PoliticaBonus\nJava puro','component');c.node(440,670,420,120,'JpaConclusaoAdapter\nAlunoRepository / CursoService','component');c.node(1000,670,420,120,'Adapter memória\n[somente nos testes]','component');c.node(40,670,300,120,'Banco relacional','database')
    c.arrow([(350,200),(440,200)]);c.arrow([(750,200),(840,200)]);c.arrow([(1150,200),(1240,200)]);c.arrow([(1395,260),(1395,410)]);c.arrow([(995,260),(995,410)])
    c.arrow([(650,670),(650,600),(930,600),(930,530)],'implementa',(-160,-30));c.arrow([(1210,670),(1210,600),(1070,600),(1070,530)],'implementa',(20,-30));c.arrow([(440,730),(340,730)]);c.save('component')
    s=Diagram('Desafio 4   Sequência da conclusão e entrega eventual',900)
    xs=[130,470,810,1150,1470]; labels=['Cliente','Core','Banco / Outbox','Worker','Receptor']
    for x,label in zip(xs,labels):
        s.node(x-110,110,220,80,label,'component');s.d.line([(x,190),(x,805)],fill='#aebac5',width=2)
    actions=[(0,1,245,'1. Concluir curso'),(1,2,330,'2. Estado + bônus + evento / COMMIT'),(1,0,415,'3. HTTP 200'),(3,2,500,'4. Ler pendentes'),(3,4,585,'5. POST eventId / timeout 2s'),(4,3,670,'6. Confirmar ou retentar'),(3,2,755,'7. Marcar entregue após confirmação')]
    for i,j,y,label in actions:
        s.arrow([(xs[i],y),(xs[j],y)]);font=ImageFont.truetype(FONT,24);box=s.d.textbbox((0,0),label,font=font);xx=(xs[i]+xs[j])/2-(box[2]-box[0])/2;s.d.rectangle((xx-6,y-35,xx+(box[2]-box[0])+6,y-5),fill='white');s.d.text((xx,y-34),label,font=font,fill='#142b40')
    s.save('sequence')
    i=Diagram('Desafio 5   C4 Container e fluxo MQTT',790)
    i.node(40,160,280,150,'Dispositivo\n[simulador]','person');i.node(490,160,320,150,'Mosquitto :1883\nSessão persistente');i.node(1060,160,460,150,'Gateway Python\nSpool durável e ACK manual');i.node(1060,505,460,150,'Core Spring Boot\nInbox idempotente + conclusão');i.node(490,505,350,150,'Banco relacional\nInbox / bônus / outbox','database')
    i.arrow([(320,235),(490,235)],'QoS 1',(-140,-40));i.arrow([(810,235),(1060,235)],'MQTT',(-175,-40));i.arrow([(1290,310),(1290,505)],'HTTP evento',(20,-110));i.arrow([(1060,580),(840,580)],'Transação',(20,-40));i.arrow([(1130,505),(950,430),(950,310)],'ACK após 2xx',(-160,-40));i.save('iot')
    d=Diagram('Desafio 6   C4 Deployment no Windows local',900)
    d.d.rounded_rectangle((25,90,1575,825),radius=15,outline='#8b9cab',width=3);d.d.text((55,105),'Todos os listeners restritos a 127.0.0.1',font=ImageFont.truetype(FONT,24),fill='#41556a')
    d.node(50,200,320,160,'Jenkins :8081\n3 pipelines\nTeste · Build · Deploy');d.node(600,180,370,150,'Core JVM :8080\nJAR + health');d.node(1150,180,370,150,'Python IA :8001\nZIP + health');d.node(1150,475,370,150,'Python integrações :8002\nZIP + SQLite');d.node(600,475,370,150,'Prometheus :9090\nScrape 5s');d.node(50,475,320,150,'Grafana :3000\nDashboard');d.node(1150,700,370,90,'Mosquitto :1883')
    d.arrow([(370,250),(600,250)],'JAR',(-170,-40));d.arrow([(370,300),(440,385),(1335,385),(1335,330)],'ZIP / independente',(-320,-35));d.arrow([(970,250),(1150,250)],'HTTP',(-135,-40));d.arrow([(970,300),(1040,400),(1040,550),(1150,550)],'HTTP',(0,-40));d.arrow([(785,475),(785,330)],'Métricas',(25,40));d.arrow([(370,550),(600,550)],'PromQL',(-180,-40));d.arrow([(1335,700),(1335,625)],'MQTT',(25,25));d.arrow([(1335,385),(1480,385),(1480,475)],'ZIP',(-50,-55));d.save('deployment')

if __name__=='__main__': generate()
