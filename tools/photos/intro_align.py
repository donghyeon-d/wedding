# photo_v3/intro1~3 → 같은 화각(intro3 기준)으로 정렬한 2400×1600 컷 + 흑백/부케 컬러 버전
# 실행: python3 -m venv .venv && .venv/bin/pip install opencv-python-headless numpy && .venv/bin/python tools/photos/intro_align.py
import cv2, numpy as np, os
P='/home/dongchoi/wedding/web/photo_v3/'; OUT='/home/dongchoi/wedding/web/src/assets/'
S=None  # 디버그용 마스크 저장 경로 (None이면 저장 안 함)
ims=[cv2.imread(P+f'intro{i}.JPG') for i in (1,2,3)]
h,w=ims[2].shape[:2]
sc=0.25
def gray(im): return cv2.cvtColor(cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY)
sift=cv2.SIFT_create(10000)
kr,dr=sift.detectAndCompute(gray(ims[2]),None)
warped=[]
for i in (0,1):
    k,d=sift.detectAndCompute(gray(ims[i]),None)
    m=cv2.BFMatcher().knnMatch(d,dr,k=2)
    good=[a for a,b in m if a.distance<0.75*b.distance]
    src=np.float32([k[a.queryIdx].pt for a in good])/sc; dst=np.float32([kr[a.trainIdx].pt for a in good])/sc
    H,inl=cv2.findHomography(src,dst,cv2.RANSAC,8.0,maxIters=20000,confidence=0.999)
    err=np.linalg.norm(cv2.perspectiveTransform(src[inl.ravel()==1][None],H)[0]-dst[inl.ravel()==1],axis=1)
    print(f'intro{i+1}: matches {len(good)} inliers {int(inl.sum())} reproj median {np.median(err):.1f}px (6000w)')
    # 원본 화각의 경계가 intro3 프레임을 다 덮는지 확인
    corners=cv2.perspectiveTransform(np.float32([[0,0],[w,0],[w,h],[0,h]])[None],H)[0]
    print('  src corners in ref', corners.round(0).tolist())
    warped.append(cv2.warpPerspective(ims[i],H,(w,h),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,0,255)))
warped.append(ims[2])
# 노출·색 맞추기: intro3 기준으로 채널별 평균/표준편차를 살짝 맞춤
ref=warped[2].reshape(-1,3).astype(np.float32); rm,rs=ref.mean(0),ref.std(0)
outs=[]
for i,im in enumerate(warped):
    f=im.astype(np.float32)
    if i<2:
        m,s=f.reshape(-1,3).mean(0),f.reshape(-1,3).std(0)
        f=(f-m)*(rs/s)+rm
        print(f'intro{i+1} color adj mean {m.round(1)} -> {rm.round(1)}')
    outs.append(np.clip(f,0,255).astype(np.uint8))
for i,im in enumerate(outs):
    small=cv2.resize(im,(2400,1600),interpolation=cv2.INTER_AREA)
    cv2.imwrite(OUT+f'intro/{i+1}.jpg',small,[cv2.IMWRITE_JPEG_QUALITY,90])
    # 흑백 + 핑크 부케만 컬러 (기존 intro-mono 톤: gray = 1.12*Y - 10.5)
    hsv=cv2.cvtColor(small,cv2.COLOR_BGR2HSV)
    Hh,Ss,Vv=hsv[...,0].astype(np.float32),hsv[...,1].astype(np.float32),hsv[...,2].astype(np.float32)
    mask=((Hh>=140)&(Hh<=178)&(Ss>=70)&(Vv>=50)).astype(np.uint8)
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,stats,_=cv2.connectedComponentsWithStats(mask)
    keep=np.zeros_like(mask)
    big=[j for j in range(1,n) if stats[j,cv2.CC_STAT_AREA]>=1500]
    for j in big: keep[lab==j]=1
    keep=cv2.dilate(keep,np.ones((9,9),np.uint8))
    keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
    a=cv2.GaussianBlur(keep.astype(np.float32),(0,0),4)[...,None]
    a=a*((Hh>=130)|(Hh<=5))[...,None]  # 부케 주변의 비(非)핑크 픽셀은 흑백 유지
    a=cv2.GaussianBlur(a,(0,0),1.5)[...,None] if a.ndim==2 else cv2.GaussianBlur(a[...,0],(0,0),1.5)[...,None]
    y=small.astype(np.float32)@np.float32([0.114,0.587,0.299])
    g=np.clip(1.12*y-10.5,0,255)[...,None].repeat(3,2)
    mono=g*(1-a)+small.astype(np.float32)*a
    print(f'mono {i+1}: bouquet blobs {len(big)} areas {[int(stats[j,cv2.CC_STAT_AREA]) for j in big]}')
    cv2.imwrite(OUT+f'intro-mono/{i+1}.jpg',np.clip(mono,0,255).astype(np.uint8),[cv2.IMWRITE_JPEG_QUALITY,90])
    if S: cv2.imwrite(S+f'/mask{i+1}.jpg',(a[...,0]*255).astype(np.uint8))
