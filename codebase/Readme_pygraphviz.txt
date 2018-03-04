1. Graphviz  설치
	http://www.graphviz.org/Download..php에서 windows install package,  .msi file  설치(경로는  C 드라이브  program files (x86), e.g. C:\Program Files (x86))

2. Anaconda 환경 구축
	Anaconda prompt 실행 후 
	conda create -n python34 python=3.4 anaconda 커맨드 (python 3.4 버전 구축)

3. 해당 환경 실행
	activate python34 커맨드

4. http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygraphviz 에서 pygraphviz?1.3.1?cp34?none?win_amd64.whl 파일 설치
	anaconda prompt에서 설치된 디렉토리로 이동 후 pip install pygraphviz-1.3.1-cp34-none-win_amd64.whl 커맨드

5. 시스템- 고급설정-환경변수 시스템변수 Path 편집, C:\Program Files (x86)\Graphviz2.38\bin 추가 (graphviz2.38의 bin folder directory)

6. Anaconda 재시동 후 activate python34

7. jupyter notebook (3) 유의/더미 설비 도출 분석 수행 까지 완료한 후 anaconda prompt codebase로 이동하여 python test2.py 커맨드
