# coding:utf-8
from __future__ import division
import numpy as np
import os
import json

def prepareData(path):
	trainO=[]
	trainS=[]
	charDict={}
	charCount=0
	i=0
	for filename in os.listdir(path):
		pragraphs=open(path+'/'+filename,'r').readlines()
		word_list=[pragraph.rstrip().split() for pragraph in pragraphs]
		tempO=[]
		tempS=[]
		i+=1
		if i%10==0: print i
		for word in word_list:
			if len(word)==1:
				tempS.append('S')
			elif len(word)==2:
				tempS.append('BE')
			else:
				tempS.append('B'+'M'*(len(word)-2)+'E')
			for char in word:
				if char not in charDict.keys():
					charDict[char]=charCount
					charCount+=1
				tempO.append(charDict[char])
					

			trainO.append(tempO)
			trainS.append(''.join(tempS))

	return trainO,trainS,charDict


class HMM():
	def __init__(self,M,N):
		self.M=M
		self.N=N
		self.A=np.zeros((M,M))
		self.B=np.zeros((M,N))
		self.pi=np.zeros(M)

	# 监督训练
	def strain(self,trainO,trainS):
		assert len(trainO)==len(trainS),'length of trainO and trainS not match'
		d={'B':0,'M':1,'E':2,'S':3}
		for i in range(len(trainO)):
			self.pi[d[trainS[0][0]]]+=1
			for j in range(len(trainO[i])):
					# print d[trainS[i][j]],trainO[i][j]
					self.B[d[trainS[i][j]]][trainO[i][j]]+=1
					if j<len(trainO[i])-1:
						print j,len(trainO[i])-1
						self.A[d[trainS[i][j]],d[trainS[i][j+1]]]+=1

		# 逐行归一化
		self.A=self.A/self.A.sum(axis=1)
		self.B=self.B/self.B.sum(axis=1)
		self.pi=self.pi/self.pi.sum()
		


	def veterbi(self,O):
		# 观测序列长度
		T=len(O)
		N=self.N
		phi=np.zeros((T,N))
		# 最优路径
		I=np.zeros(T)
		# 初始化phi0 delta0
		for i in range(N):
			phi[0,i]=0
			delta[0,i]=self.pi[i]*self.B[0,O[i]]

		# 地推 动态规划
		for t in range(1,T):
			for i in range(N):
				p=np.array([phi[t-1,j]*self.A[j,i] for j in range(N)])
				phi[t,i]=p.argmax()
				delta[t,i]=p[phi[t,i]]*self.B[i,O[t]]

		prob=delta[T-1,:].max()
		I[T-1]=delta[T-1,:].argmax()

		for t in range(T-2,-1,-1):
			I[t]=phi[t+1,I[t+1]]

		return I,prob

	def toJson(self,filename):
		a=list(self.A)
		b=list(self.B)
		pi=list(self.pi)
		n=self.N
		m=self.M
		obj={'a':a,'b':b,'pi':pi,'n':n,'m':m}
		f=open(filename,'w')
		f.write(json.dumps(obj))
		f.close()

	def fromJson(self,filename):
		f=open(filename)
		s=f.read()
		obj=json.load(s)
		self.A=np.array(obj['a'])
		self.B=np.array(obj['b'])
		self.pi=np.array(obj['pi'])
		self.N=obj['n']
		self.M=obj['m']





	
def test():
	trainO,trainS,charDict=prepareData('train_data')
	print 'loading complete'
	hmm=HMM(4,len(charDict))
	hmm.train(trainO,trainS)
	O='乒乓球拍卖完了'
	nO=[charDict[s] for s in O]
	I,p=hmm.veterbi(nO)
	print I

if __name__ == '__main__':
	test()
