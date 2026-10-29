"""Pinceladas faciales dirigidas. Tonos de Luto, mate, sin sangre ni PBR fotografico."""
import numpy as np

def styles(A, original, skin_base):
    smooth=A.smoothstep
    def mix(c,color,amount):
        a=np.clip(amount,0,1)[:,None]
        return c*(1-a)+np.asarray(color)[None,:]*a
    def ell(x,z,cx,cz,rx,rz):return ((x-cx)/rx)**2+((z-cz)/rz)**2
    def line(x,z,points,width):
        d=np.full(x.shape,100.,dtype=np.float32)
        for (ax,az),(bx,bz) in zip(points,points[1:]):
            dx,dz=bx-ax,bz-az
            t=np.clip(((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz),0,1)
            d=np.minimum(d,np.hypot(x-(ax+t*dx),z-(az+t*dz)))
        return np.exp(-((d/width)**2)*1.7)
    def face(P,mask,pos,nrm,c):
        c=skin_base(P,mask,pos,nrm,c)
        x,y,z=pos.T; fr=np.clip(nrm[:,1]*1.8,0,1)
        # Capas amplias de color siguiendo anatomia; no motas uniformes por todo el rostro.
        patches=[(-.18,5.08,.10,.12,(.36,.33,.39),.20),
                 (.19,5.17,.10,.13,(.47,.40,.42),.15),
                 (.09,5.39,.17,.09,(.53,.56,.46),.12),
                 (-.07,4.96,.14,.09,(.42,.44,.42),.14)]
        for cx,cz,rx,rz,color,strength in patches:
            alpha=np.exp(-ell(x,z,cx,cz,rx,rz)*1.5)*strength*fr
            c=mix(c,color,alpha)
        grain=A.fbm(np.stack([x*33,y*42,z*11],1),3,942)
        strokes=(grain-.5)*.085
        c=np.clip(c+strokes[:,None]*fr[:,None],0,1)
        for s in (-1,1):
            ex=s*.113; ez=5.210 if s<0 else 5.220
            rz=.040 if s<0 else .026
            q=ell(x,z,ex,ez,.078,rz*1.65)
            c=mix(c,(.31,.285,.33),np.exp(-q*1.2)*.36*fr)
            # Parpado palido arriba, irritacion violeta apagada en el borde inferior.
            ey=(z-ez-(x-ex)*.07)/rz
            rim=np.exp(-((np.sqrt(np.maximum(0,ell(x,z,ex,ez,.068,rz)))-1.03)/.23)**2)*fr
            c=mix(c,(.43,.32,.35),rim*.42*(ey<.15))
            c=mix(c,(.61,.58,.53),rim*.24*(ey>.35))
            # Cejas quebradas en angustia; cada una tiene inclinacion distinta.
            if s<0: brow=[(-.205,5.270),(-.163,5.285),(-.103,5.307),(-.056,5.308)]
            else:brow=[(.051,5.305),(.102,5.290),(.165,5.280),(.204,5.285)]
            browmask=line(x,z,brow,.0075)
            dry=.70+.30*A.vnoise(np.stack([x*180,y*55,z*52],1),947)
            c=mix(c,(.16,.155,.15),browmask*dry*.78*fr)
            # Borde claro fino junto al pliegue, no ceja blanca gruesa.
            crease=[(px,pz-.015) for px,pz in brow]
            c=mix(c,(.38,.36,.36),line(x,z,crease,.0035)*.30*fr)
            highlight=[(px,pz+.010) for px,pz in brow]
            c=mix(c,(.70,.70,.63),line(x,z,highlight,.003)*.18*fr)
            tearx=s*(.11+.006*np.sin((z-5.04)*45))
            tear=np.exp(-((x-tearx)/.007)**2)*smooth(5.055,5.12,z)*smooth(5.19,5.14,z)
            c=mix(c,(.24,.24,.29),tear*.46*fr)
            # Pliegue del lagrimal al pomulo: roto y tenue, sigue el gesto.
            fold=[(s*.050,5.205),(s*.072,5.177),(s*.12,5.161),(s*.18,5.163)]
            c=mix(c,(.37,.33,.36),line(x,z,fold,.0038)*.32*fr)
        # Tres arrugas cortas, desiguales, que nacen en la contraccion del entrecejo.
        wrinkles=[([(-.086,5.347),(-.035,5.359),(.021,5.355),(.081,5.343)],.22),
                  ([(-.065,5.374),(-.010,5.383),(.046,5.373)],.15),
                  ([(-.014,5.295),(-.027,5.322),(-.018,5.342)],.25)]
        for pts,strength in wrinkles:
            c=mix(c,(.38,.38,.35),line(x,z,pts,.0028)*strength*fr)
            c=mix(c,(.70,.70,.63),line(x,z,[(a,b+.005) for a,b in pts],.0024)*strength*.65*fr)
        # Cicatriz curada estrecha en la mejilla, con bordes irregulares (sin gore).
        scar=[(.190,5.175),(.179,5.147),(.161,5.120),(.153,5.082)]
        c=mix(c,(.38,.31,.34),line(x,z,scar,.0034)*.42*fr)
        c=mix(c,(.68,.62,.59),line(x,z,[(a-.004,b) for a,b in scar],.0023)*.35*fr)
        # Aletas de nariz y comisuras con transiciones, no trazos negros pintados.
        for s in (-1,1):
            c=mix(c,(.43,.34,.35),np.exp(-ell(x,z,s*.030,5.127,.024,.026)*1.8)*.25*fr)
            groove=[(s*.035,5.120),(s*.058,5.090),(s*.075+.020,5.020)]
            c=mix(c,(.35,.32,.35),line(x,z,groove,.0045)*.27*fr)
        # Salpicaduras de pigmento escasas, pequenas y dirigidas a sienes.
        flecks=A.vnoise(np.stack([x*155,y*90,z*160],1),971)
        sparse=smooth(.81,.93,flecks)*smooth(.09,.24,np.abs(x))*.15*fr
        c=mix(c,(.34,.35,.32),sparse)
        return c
    def lips(P,mask,pos,nrm,c):
        x,y,z=pos.T
        c=mix(c,(.36,.245,.285),np.full(x.shape,.30))
        striation=.5+.5*np.sin((x-.026)*270+z*19)
        dryness=A.fbm(np.stack([x*70,y*50,z*110],1),2,981)
        c=mix(c,(.25,.20,.235),smooth(.80,.98,striation)*smooth(.45,.65,dryness)*.48)
        c=mix(c,(.58,.48,.45),smooth(.68,.86,dryness)*.28)
        return c
    def teeth(P,mask,pos,nrm,c):
        x,y,z=pos.T
        patina=A.fbm(pos*65,2,982)
        c=mix(c,(.39,.34,.25),smooth(.57,.78,patina)*.32)
        return c
    def eyes(P,mask,pos,nrm,c):
        x,y,z=pos.T
        edge=np.clip(1-nrm[:,1],0,1)
        c=mix(c,(.52,.44,.43),edge*.15)
        # Ojo derecho mas opaco; izquierdo mantiene la direccion de la mirada.
        c=mix(c,(.64,.67,.60),(x>0)*.20)
        return c
    def iris(P,mask,pos,nrm,c):
        x,y,z=pos.T
        cx=np.where(x<0,-.101,.103); cz=np.where(x<0,5.205,5.215)
        angle=np.arctan2(z-cz,x-cx)
        radial=(np.sin(angle*13)+np.sin(angle*29+.5))*.5
        c*=1+.10*radial[:,None]
        return c
    result={k:dict(v) for k,v in original.items()}
    result['cara'].update(extra=face,var=.07,stroke=(1,1,2.5),stroke_scale=14,blotch=.065,ao=.40,light=.20,face_var=.025)
    result['piel']['extra']=skin_base
    result['labio'].update(extra=lips,base='#62505a',ao=.20,light=.10,var=.06)
    result['diente'].update(extra=teeth,base='#aba187',ao=.25,light=.12)
    result['ojo'].update(extra=eyes,base='#b6b69e',ao=.18,light=.08)
    result['iris']=dict(base='#777d69',var=.03,ao=.1,light=.06,extra=iris)
    result['pupila']=dict(base='#242622',var=.015,ao=.08,light=.03)
    result['reflejo']=dict(base='#d9d8bd',var=0,ao=0,light=0)
    return result
