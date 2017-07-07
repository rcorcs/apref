#APReF: Automatic Parallelizer of REcursive Functions

from sets import Set

import sys
import re

from sympy import solve, Symbol, sympify

debugMode=False

foldr1 = 'foldr1'

numericTypes = ['Integer','Rational','Floating','RealFloat','Num','Integral','Fractional']
booleanTypes = ['Boolean']
supportedTypes = ['Integer']

def setDebugMode(state):
   global debugMode
   debugMode = state

def setFoldr1(cmd):
  global foldr1
  foldr1 = cmd

def getFoldr1():
  global foldr1
  return foldr1



def inverse(string, left_string=None):
   string = '-' + string
   e = sympify(string.replace('=','+'))
   if left_string:
      symbols = e.free_symbols
      ans = left_string + ' = ' + str(solve(e, sympify(left_string))[0])
   else:
      left = sympify(string.split('=')[0].strip().replace('-',''))
      symbols = e.free_symbols
      symbols.remove( left )
      right = list(symbols)[0]
      ans = str(right) + ' = ' + str(solve(e, right)[0])
   return ans

def hopFunction(hop, x, base):
   if '_HOP_'+x not in re.split('[^_a-zA-Z0-9]', hop):
      if debugMode:
         print 'h('+x+') = '+hop
         print 'h^k('+x+') = '+base   
      hop_inv = inverse('_HOP_'+x+' = '+hop, x)
      if debugMode:
         print hop_inv
      return (str(hop_inv).split('=')[1].strip(), '_HOP_'+x)
   return None

def funcComposition(func, x, k):
   f = sympify(func)
   fc = sympify(func)
   for i in xrange(k):
      fc = fc.subs({x:f})
   return fc

def funcVariableComposition(func, x, k):
   f5 = funcComposition(func, x, 5)
   f7 = funcComposition(func, x, 7)
   var5 = Set(re.split('[^_a-zA-Z0-9]', ' '+str(f5)+' ')).difference(Set(re.split('[^_a-zA-Z0-9]', str(f5))).intersection(Set(re.split('[^_a-zA-Z0-9]', str(f7)))))
   if len(var5)==1:
      var7 = Set(re.split('[^_a-zA-Z0-9]', ' '+str(f7)+' ')).difference(Set(re.split('[^_a-zA-Z0-9]', str(f5))).intersection(Set(re.split('[^_a-zA-Z0-9]', str(f7)))))
      var5 = str(list(var5)[0])
      var7 = str(list(var7)[0])
      sf5 = str(f5)
      sf7 = str(f7)
      for i in xrange(len(sf5)):
         if sf5[i]!=sf7[i] and sf5[i]==var5[0] and sf7[i]==var7[0]:
            return sf5[:i]+k+sf5[i+len(var5):]
   return None

def funcSolve(func, x, val):
   f = sympify(func)
   return f.subs({x:val})

def findCloseChar(source, idx, openChar, closeChar):
   #print source
   count = 1
   while count>0:
      if idx<0 or idx>=len(source):
         return -1
      if source[idx]==openChar:
         count += 1
      elif source[idx]==closeChar:
         count -= 1
      idx += 1
   return idx

def sortOperators(operators):
   if '+' in operators and '*' in operators and len(operators)==2:
      return ['+','*']
   else:
      return None

def parseTypeDef(code):
   code = code.strip()
   type = None
   if '::' in code and '->' in code:
      name = code.split('::')[0].strip()
      tmp = code.split('::')[1].split('->')
      #assert len(tmp)==2, 'ERROR: unsupported definition: '+code.strip()
      if len(tmp)!=2:
         return None
      domain = tmp[0].strip()
      image = tmp[1].strip()
      if debugMode:
         print 'Function:',name
         print 'Domain:',domain
         print 'Image:',image
      type = {'name':name,'domain':domain,'image':image}
   return type

def countRecursiveCalls(name, expr):
   recursiveCallMatches = list(re.findall('[^_A-Za-z0-9]'+name+'[ \t]*\(', expr))
   recursiveCallMatches.extend(list(re.findall('^'+name+'[ \t]*\(', expr)))
   return len(recursiveCallMatches)

def parseRecursiveBase(code):
   left = code.split('=')[0].split()
   #assert len(left)==2, 'ERROR: Expected function with one argument.\n'+code.strip()
   if len(left)!=2:
      return None

   name = left[0].strip()
   arg = left[1].strip()
   expr = code.split('=')[1].strip()
   return {'name':name,'arg':arg,'expr':expr}

def parseRecursion(code):
   lops = []
   rops = []
 
   g_1 = None
   g_2 = None
   g_3 = None
   g_4 = None

   left = code.split('=')[0].split()
   #assert len(left)==2, 'ERROR: Expected function with one argument.\n'+code.strip()
   if len(left)!=2:
      return None
   name = left[0].strip()
   arg = left[1].strip()

   right = code.split('=')[1].strip()
   rexpr = None
   if len(re.findall('[^_A-Za-z0-9]'+name+'[ \t]*\(', right))>0:
      rexpr = '[^_A-Za-z0-9]'+name+'[ \t]*\('
   if len(re.findall('^'+name+'[ \t]*\(', right))>0:
      rexpr = '^'+name+'[ \t]*\('
   if rexpr==None:
      return None
   for m in re.finditer(rexpr, right):
      endRecursiveCall = findCloseChar(right, m.end(0), '(', ')')
      lexpr = right[:m.start(0)].strip()
      rexpr = right[endRecursiveCall:].strip()
      if debugMode:
         print 'recursive call:',right[m.start(0):endRecursiveCall]
         print 'lexpr:',lexpr
         print 'rexpr:',rexpr
      hop = right[m.end(0):endRecursiveCall-1]
      if len(lexpr.strip())>0:
         ops = []
         for mop in re.finditer('[+\-\*/][+\-\*/]*', lexpr):
            opidx = mop.start(0)
            j = opidx-1
            ignoreop = False
            while j>=0:
               if lexpr[j]=='(':
                  endidx = findCloseChar(lexpr, j+1, '(', ')')
                  if endidx>mop.end(0):
                     ignoreop = True
                     break
               j = j - 1
            op = mop.group(0)
            if ignoreop or len(op.strip())==0:
               continue
            ops.append(op.strip())
         if debugMode:
            print 'ops:',ops
         if len(Set(ops))>2:
            print 'ERROR: Format not supported. Operators found 1:',ops
            print code
            return None
         lops = [ops[0]]
         if len(Set(ops))==2:
            lops.append(ops[-1])

         if debugMode:
            print 'lops:',set(lops)

         if len(lops)==2:
            g1idx = lexpr.rfind(lops[0])
            ignoreop = True
            while ignoreop:
               j = g1idx-1
               ignoreop = False
               while j>=0:
                  if lexpr[j]=='(':
                     endidx = findCloseChar(lexpr, j+1, '(', ')')
                     #print 'Found ( in',j,endidx,g1idx
                     if endidx>g1idx:
                        ignoreop = True
                        break
                  j = j - 1
               if ignoreop:
                  g1idx = lexpr[:g1idx-1].rfind(lops[0])

            if debugMode:
               print 'g_1('+arg+') = '+lexpr[:g1idx].strip()
            g_1 = lexpr[:g1idx].strip()
            if debugMode:
               print 'g_3('+arg+') = '+lexpr[g1idx+len(lops[0]):-len(lops[1])].strip()
            g_3 = lexpr[g1idx+len(lops[0]):-len(lops[1])].strip()
         else:
            g_1 = lexpr[:-len(lops[0])].strip()
            if debugMode:
               print 'g_1('+arg+') = '+g_1
      if len(rexpr.strip())>0:
         ops = []
         for mop in re.finditer('[+\-\*/][+\-\*/]*', rexpr):
            opidx = mop.start(0)
            j = opidx-1
            ignoreop = False
            while j>=0:
               if rexpr[j]=='(':
                  endidx = findCloseChar(rexpr, j+1, '(', ')')
                  if endidx>mop.end(0):
                     ignoreop = True
                     break
               j = j - 1
            op = mop.group(0)
            if ignoreop or len(op.strip())==0:
               continue
            ops.append(op.strip())
         if debugMode:
            print 'ops:',ops
         if len(Set(ops))>2:
            print 'ERROR: Format not supported. Operators found 3:',ops
            print code
            return None
         rops = [ops[0]]
         if len(Set(ops))==2:
            rops.append(ops[-1])

         if len(rops)==2:
            g2idx = rexpr.find(rops[1])
            ignoreop = True
            while ignoreop:
               j = g2idx-1
               ignoreop = False
               while j>=0:
                  if rexpr[j]=='(':
                     endidx = findCloseChar(rexpr, j+1, '(', ')')
                     if endidx>g2idx:
                        ignoreop = True
                        break
                  j = j - 1
               if ignoreop:
                  g2idx = rexpr[g2idx+1:].find(rops[1])
            if debugMode:
               print 'g_2('+arg+') = '+rexpr[g2idx+len(rops[1]):].strip()
            g_2 = rexpr[g2idx+len(rops[1]):].strip()
            if debugMode:
               print 'g_4('+arg+') = '+rexpr[len(rops[0]):g2idx].strip()
            g_4 = rexpr[len(rops[0]):g2idx].strip()
         else:
            g_2 = rexpr.strip()[len(rops[0]):].strip()
            if debugMode:
               print 'g_2('+arg+') = '+g_2
   if max(len(lops),len(rops))>2:
      print 'ERROR: Format not supported. Operators found 5:',ops
      print code
      return None
   if debugMode:
      print 'g_3:',g_3
      print 'g_4:',g_4
      print 'lops U rops:',Set(lops).union(Set(rops))

   result = {'name':name, 'arg':arg, 'hop-expr':hop, 'algebraic-type':None, 'exprs':[],'operators':[]}
   
   if (not g_3) and (not g_4) and len(Set(lops).union(Set(rops)))==1:
      result['algebraic-type'] = 'monoid'
      result['exprs'] = [g_1,g_2]
      result['operators'] = [lops[0]]
   elif len(Set(lops).union(Set(rops)))==2:
      result['algebraic-type'] = 'semiring'

      if len(lops)==2:
         result['operators'] = [lops[0],lops[1]]
      elif len(rops)==2:
         result['operators'] = [rops[1],rops[0]]
      else:
         result['operators'] = sortOperators(list(Set(lops).union(Set(rops))))
         if result['operators']==None:
            print 'ERROR: Operators not supported:',list(Set(lops).union(Set(rops)))
            print code
            return None

      if len(lops)==1:
         if g_1 and lops[0]==result['operators'][1]:
            g_3 = g_1
            g_1 = None
      if len(rops)==1:
         if g_2 and rops[0]==result['operators'][1]:
            g_4 = g_2
            g_2 = None

      result['exprs'] = [g_1,g_2,g_3,g_4]

   else:
      print 'ERROR: Format not supported. Operators found 5:',ops
      print code
      return None
   return result

def rewriteTerm(expr,arg,solvedHop):
   term = None
   if expr:
      term = ' '+expr+' '
      for i in xrange(len(re.findall('[^_A-Za-z0-9]'+arg+'[^_A-Za-z0-9]', term))):
         for m in re.finditer('[^_A-Za-z0-9]'+arg+'[^_A-Za-z0-9]', term):
            term = term[:m.start(0)+1]+'('+str(solvedHop)+')'+term[m.end(0)-1:]
            break
      term = term.strip()
   return term

def hasUseOf(term, arg):
   return (len(re.findall('[^_A-Za-z0-9]'+arg+'[^_A-Za-z0-9]', term))>0)

def isConstantFunction(func):
   tmp = func.split('=')
   if len(tmp)==2:
      args = tmp[0].split()[1:]
      term = tmp[1].strip()
      return all([ (not hasUseOf(term, arg)) for arg in args ])
   else:
      return False

def rewriteMonoidCode(type,base,recursion,optimizeConstants=True):
   if debugMode:
      print 'Monoid-based recursive function'
   binop = recursion['operators'][0]
   name = type['name']

   rewritten = ''

   kComposedHop = funcVariableComposition(recursion['hop-expr'],recursion['arg'],'_HOP_k')
   if debugMode:
      print 'k-composed hop:',str(kComposedHop)+' = '+base['arg']
   solvedHopComposition = inverse(base['arg']+' = '+kComposedHop, '_HOP_k')
   if debugMode:
      print 'solved k-composed hop:',solvedHopComposition
   #sanity check
   if str(solvedHopComposition).split('=')[0].strip()!='_HOP_k':
      return None
   hop_k = str(solvedHopComposition).split('=')[1].strip()
   if debugMode:
      print 'hop_k:','('+hop_k+')'

   hop_inv = hopFunction(recursion['hop-expr'], recursion['arg'], base['arg'])
   if debugMode:
      print 'hop inverse:',hop_inv

   iComposedHopInverse = funcVariableComposition(hop_inv[0],hop_inv[1],'_HOP_i')
   if debugMode:
      print 'i-composed hop inverse:',iComposedHopInverse
   solvedHopComposition = funcSolve(iComposedHopInverse, hop_inv[1], base['arg'])
   if debugMode:
      print 'solved i-composed hop inverse:',solvedHopComposition

   terms = [rewriteTerm(term,recursion['arg'],solvedHopComposition) for term in recursion['exprs']]

   if debugMode:
     print 'Rewriting Code'
   s = ''
   kvar = 'k'
   if recursion['arg']==kvar:
      kvar = name+'_k'

   if terms[0]:
      rewritten += name+'_g_1 _HOP_i = '+terms[0]+'\n'
      s += '('+foldr1+' ('+binop+') (map '+name+'_g_1 (reverse [1..'+kvar+']))) '+binop+' '

   s += base['expr']

   if terms[1]:
      rewritten += name+'_g_2 _HOP_i = '+terms[1]+'\n'
      s += ' '+binop+' ('+foldr1+' ('+binop+') (map '+name+'_g_2 [1..'+kvar+']))'

   #rewritten += name+' :: '+type['domain']+' -> '+type['image']+'\n'
   rewritten += type['src'].strip()+'\n'
   rewritten += base['src'].strip()+'\n'
   rewritten += name+' '+recursion['arg']+' = let '+kvar+' = '+hop_k+' in '+s
   return rewritten

def rewriteSemiringCode(type,base,recursion,useScan=True,optimizeConstants=True):
   if debugMode:
      print 'Semiring-based recursive function'
   binopAdd = recursion['operators'][0]
   binopMult = recursion['operators'][1]
   name = type['name']

   rewritten = ''


   kComposedHop = funcVariableComposition(recursion['hop-expr'],recursion['arg'],'_HOP_k')
   if debugMode:
      print 'k-composed hop:',str(kComposedHop)+' = '+base['arg']
   solvedHopComposition = inverse(base['arg']+' = '+kComposedHop, '_HOP_k')
   if debugMode:
      print 'solved k-composed hop:',solvedHopComposition
   #sanity check
   if str(solvedHopComposition).split('=')[0].strip()!='_HOP_k':
      return None
   hop_k = str(solvedHopComposition).split('=')[1].strip()
   if debugMode:
      print 'hop_k:','('+hop_k+')'

   hop_inv = hopFunction(recursion['hop-expr'], recursion['arg'], base['arg'])
   if debugMode:
      print 'hop inverse:',hop_inv

   iComposedHopInverse = funcVariableComposition(hop_inv[0],hop_inv[1],'_HOP_i')
   if debugMode:
      print 'i-composed hop inverse:',iComposedHopInverse
   solvedHopComposition = funcSolve(iComposedHopInverse, hop_inv[1], base['arg'])
   if debugMode:
      print 'solved i-composed hop inverse:',solvedHopComposition

   terms = [rewriteTerm(term,recursion['arg'],solvedHopComposition) for term in recursion['exprs']]

   constTerms = [False for _ in terms]


   if debugMode:
     print 'Rewriting Code'
   s = ''
   for t in xrange(len(terms)):
      if terms[t]:
         func = name+'_g_'+str(t+1)+' _HOP_i = '+terms[t]
         rewritten += str(func)+'\n'
         constTerms[t] = optimizeConstants and isConstantFunction(func)

   if debugMode:
      print 'Constant terms:',constTerms
   eliminateWScan = False
   eliminateVScan = False

   if constTerms[2]:
      if (type['image'] in numericTypes) and binopMult=='*':
         eliminateVScan = True
      elif (type['image'] in booleanTypes):
         eliminateVScan = True
   if constTerms[3]:
      if (type['image'] in numericTypes) and binopMult=='*':
         eliminateWScan = True
      elif (type['image'] in booleanTypes):
         eliminateWScan = True


   betas = [False,False]
   for t in [0,1]:
       if terms[t]:
      #if (terms[2] and terms[t]) or terms[3]:
         betas[t] = True
         if useScan: 
            vArg = name+'_BETA_v'
            if (eliminateVScan and constTerms[2]) or (not terms[2]):
               vArg = ''
            wArg = name+'_BETA_w'
            if (eliminateWScan and constTerms[3]) or (not terms[3]):
               wArg = ''
            s = name+'_BETA_'+str(t+1)+' '+vArg+' '+wArg+' '+name+'_BETA_k '+name+'_BETA_i = '
            if terms[2] and terms[t]:
               if constTerms[2]:
                  if (type['image'] in numericTypes) and binopMult=='*':
                     s += '(('+name+'_g_3 0)^('+name+'_BETA_k-'+name+'_BETA_i))'+binopMult
                  elif (type['image'] in booleanTypes):
                     s += '('+name+'_g_3 0)'+binopMult
                  else:
                     eliminateVScan = False
                     
                     s += '('+name+'_BETA_v!!(fromIntegral ('+name+'_BETA_i-1)))'+binopMult
               else:
                  eliminateVScan = False
                  s += '('+name+'_BETA_v!!(fromIntegral ('+name+'_BETA_i-1)))'+binopMult
               #s += '('+name+'_g_'+str(t+1)+' '+name+'_BETA_i)'
            s += '('+name+'_g_'+str(t+1)+' '+name+'_BETA_i)'
            if terms[3]:
               s += binopMult
               #if terms[2] and terms[t]:
               #   s += binopMult
               if constTerms[3]:
                  if (type['image'] in numericTypes) and binopMult=='*':
                     s += '(('+name+'_g_4 0)^('+name+'_BETA_k-'+name+'_BETA_i))'
                  elif (type['image'] in booleanTypes):
                     s += '('+name+'_g_4 0)'
                  else:
                     eliminateWScan = False
                     s += '('+name+'_BETA_w!!(fromIntegral (('+name+'_BETA_k-'+name+'_BETA_i)-1)))'
               else:
                  eliminateWScan = False
                  s += '('+name+'_BETA_w!!(fromIntegral (('+name+'_BETA_k-'+name+'_BETA_i)-1)))'
         else:
            s = name+'_BETA_'+str(t+1)+' '+name+'_BETA_k '+name+'_BETA_i = '
            if terms[2] and terms[t]:
               s += '(foldr1 ('+binopMult+') (map '+name+'_g_3 (reverse [('+name+'_BETA_i+1)..'+name+'_BETA_k])))'+binopMult
               #s += '('+name+'_g_'+str(t+1)+' '+name+'_BETA_i)'
            s += '('+name+'_g_'+str(t+1)+' '+name+'_BETA_i)'
            if terms[3]:
               s += binopMult
               #if terms[2] and terms[t]:
               #   s += binopMult
               s += '(foldr1 ('+binopMult+') (map '+name+'_g_4 [('+name+'_BETA_i+1)..'+name+'_BETA_k]))'
         rewritten += s+'\n'

   if useScan:
      vArg = 'v'
      if (eliminateVScan and constTerms[2]) or (not terms[2]):
         vArg = ''
      wArg = 'w'
      if (eliminateWScan and constTerms[3]) or (not terms[3]):
         wArg = ''

      phi_1 = False
      if terms[0] or betas[0]:
         phi_1 = True
         s = name+'_PHI_1 '+vArg+' '+wArg+' k = '
         if terms[0]:
            s += '('+name+'_g_1 k) '
         if terms[0] and betas[0]:
            s += binopAdd+' '
         if betas[0]:
            s += '('+foldr1+' ('+binopAdd+') (map ('+name+'_BETA_1 '+vArg+' '+wArg+' k) (reverse [1..(k-1)])))'
         rewritten += s+'\n'

      phi_2 = False
      if terms[1] or betas[1]:
         phi_2 = True
         s = name+'_PHI_2 '+vArg+' '+wArg+' k = '
         if betas[1]:
            s += '('+foldr1+' ('+binopAdd+') (map ('+name+'_BETA_2 '+vArg+' '+wArg+' k) [1..(k-1)]))'
         if terms[1] and betas[1]:
            s += ' '+binopAdd+' '
         if terms[1]:
            s += '('+name+'_g_2 k)'
         rewritten += s+'\n'

      phi_3 = False
      if terms[2]:
         phi_3 = True
         readV1AndMult = '(v!!0)'+binopMult
         if constTerms[2]:
            if (type['image'] in numericTypes) and binopMult=='*':
               readV1AndMult = '('+name+'_g_3 0)^(k-1)'+binopMult
            elif (type['image'] in booleanTypes):
               readV1AndMult = ''
            else:
               eliminateVScan = False
            rewritten += name+'_PHI_3 '+vArg+' '+wArg+' k = '+readV1AndMult+'('+name+'_g_3 1)\n'
         else:
            eliminateVScan = False
            rewritten += name+'_PHI_3 '+vArg+' '+wArg+' k = (v!!0)'+binopMult+'('+name+'_g_3 1)\n'

      phi_4 = False
      if terms[3]:
         phi_4 = True
         readWK1AndMult = binopMult+'(w!!(fromIntegral (k-2)))'
         if constTerms[3]:
            if (type['image'] in numericTypes) and binopMult=='*':
               readWK1AndMult = binopMult+'('+name+'_g_4 0)^(k-1)'
            elif (type['image'] in booleanTypes):
               readWK1AndMult = ''
            else:
               eliminateWScan = False
            rewritten += name+'_PHI_4 '+vArg+' '+wArg+' k = ('+name+'_g_4 1)'+readWK1AndMult+'\n'
         else:
            eliminateWScan = False
            rewritten += name+'_PHI_4 '+vArg+' '+wArg+' k = ('+name+'_g_4 1)'+binopMult+'(w!!(fromIntegral (k-2)))\n'

      kvar = 'k'
      if recursion['arg']==kvar:
         kvar = name+'_k'
      vvar = 'v'
      if recursion['arg']==vvar:
         vvar = name+'_v'
      if (eliminateVScan and constTerms[2]) or (not terms[2]):
         vvar = ''
      wvar = 'w'
      if recursion['arg']==wvar:
         wvar = name+'_w'
      if (eliminateWScan and constTerms[3]) or (not terms[3]):
         wvar = ''

      #rewritten += name+' :: '+type['domain']+' -> '+type['image']+'\n'
      rewritten += type['src'].strip()+'\n'
      rewritten += base['src'].strip()+'\n'
      s = name+' '+recursion['arg']+' = '
      s += 'let '+kvar+' = '+hop_k
      if terms[2] and ((not constTerms[2]) or (not eliminateVScan)):
         s += '; '+vvar+' = scanr1 ('+binopMult+') (map '+name+'_g_3 (reverse [2..'+kvar+']))'

      if terms[3]!=None and ((not constTerms[3]) or (not eliminateWScan)):
         s += '; '+wvar+' = scanl1 ('+binopMult+') (map '+name+'_g_4 [2..'+kvar+'])'
      s += '\n in '
      if phi_1:
         s += '('+name+'_PHI_1 '+vvar+' '+wvar+' '+kvar+')'+binopAdd
      if phi_3:
         s += '('+name+'_PHI_3 '+vvar+' '+wvar+' '+kvar+')'+binopMult
      s += '('+base['expr']+')'
      if phi_4:
         s += binopMult+'('+name+'_PHI_4 '+vvar+' '+wvar+' '+kvar+')'
      if phi_2:
         s += binopAdd+'('+name+'_PHI_2 '+vvar+' '+wvar+' '+kvar+')'
      rewritten += s
   else:
      phi_1 = False
      if terms[0] or betas[0]:
         phi_1 = True
         s = name+'_PHI_1 k = '
         if terms[0]:
            s += '('+name+'_g_1 k) '
         if terms[0] and betas[0]:
            s += binopAdd+' '
         if betas[0]:
            s += '('+foldr1+' ('+binopAdd+') (map ('+name+'_BETA_1 k) (reverse [1..(k-1)])))'
         rewritten += s+'\n'

      phi_2 = False
      if terms[1] or betas[1]:
         phi_2 = True
         s = name+'_PHI_2 k = '
         if betas[1]:
            s += '('+foldr1+' ('+binopAdd+') (map ('+name+'_BETA_2 k) [1..(k-1)]))'
         if terms[1] and betas[1]:
            s += ' '+binopAdd+' '
         if terms[1]:
            s += '('+name+'_g_2 k)'
         rewritten += s+'\n'

      phi_3 = False
      if terms[2]:
         phi_3 = True
         rewritten += name+'_PHI_3 k = ('+foldr1+' ('+binopMult+') (map '+name+'_g_3 (reverse [1..k])))\n'

      phi_4 = False
      if terms[3]:
         phi_4 = True
         rewritten += name+'_PHI_4 k = ('+foldr1+' ('+binopMult+') (map '+name+'_g_4 [1..k]))\n'

      kvar = 'k'
      if recursion['arg']==kvar:
         kvar = name+'_k'

      #rewritten += name+' :: '+type['domain']+' -> '+type['image']+'\n'
      rewritten += type['src'].strip()+'\n'
      rewritten += base['src'].strip()+'\n'
      s = name+' '+recursion['arg']+' = '
      s += 'let '+kvar+' = '+hop_k+' in '
      if phi_1:
         s += '('+name+'_PHI_1 '+kvar+')'+binopAdd
      if phi_3:
         s += '('+name+'_PHI_3 '+kvar+')'+binopMult
      s += '('+base['expr']+')'
      if phi_4:
         s += binopMult+'('+name+'_PHI_4 '+kvar+')'
      if phi_2:
         s += binopAdd+'('+name+'_PHI_2 '+kvar+')'
      rewritten += s
   while '  ' in rewritten:
      rewritten = rewritten.replace('  ',' ')
   return rewritten

def rewriteCode(type,base,recursion,useScan=True,optimizeConstants=True):
   if recursion['algebraic-type']=='monoid':
      return rewriteMonoidCode(type,base,recursion)
   elif recursion['algebraic-type']=='semiring':
      return rewriteSemiringCode(type,base,recursion,useScan,optimizeConstants)
   else:
      return None

def hasUnsupportedConstructions(code):
   keywords = ['let','where','case','import']
   isUnsupported = any([ len(re.findall('[^_A-Za-z0-9]'+kw+'[^_A-Za-z0-9]', code))>0 for kw in keywords])
   isUnsupported = isUnsupported or any([ len(re.findall('^'+kw+'[^_A-Za-z0-9]', code))>0 for kw in keywords])
   return isUnsupported

def parallelize(code,useScan=True,optimizeConstants=True):
   name = None
   type = None
   base = None
   recursion = None

   for linesrc in code.split('\n'):
      line = linesrc.strip()
      assert (not hasUnsupportedConstructions(line)), 'ERROR: Unsupported construction:\n'+line.strip()
      if '::' in line and '->' in line:
         type = parseTypeDef(line)
         assert type!=None,'ERROR: Error while parsing type definition'
         name = type['name']
         assert (type['domain'] in supportedTypes), 'ERROR: unsupported domain type: '+str(type['domain'])+'. Types expected:'+str(supportedTypes)
         type['src'] = linesrc+'\n'
      elif '=' in line:
         left = line.split('=')[0].strip()
         right = line.split('=')[1].strip()
         if not name:
            name = left.strip().split()[0].strip()
         assert type!=None,'ERROR: Type for function '+name+' not defined. Type inference not supported yet.'
         assert line.strip().split()[0]==name,'ERROR: function '+name+' mismatch with:\n>>\t'+line.strip()
         numOfRecursiveCalls = countRecursiveCalls(name, right)
         assert numOfRecursiveCalls<2,'ERROR: Multiple recursive calls to function '+name+'\n'+line.strip()
         if numOfRecursiveCalls==0:
            base = parseRecursiveBase(line)
            assert base!=None,'ERROR: Error while parsing base definition'
            #sanity check
            assert base['name']==type['name'],'ERROR: function '+name+' mismatch with:\n>>\t'+line.strip()
            baseX = base['arg']
            baseY = base['expr']
            if debugMode:
               print 'Base Arg:',baseX
               print 'Base Expr:',baseY
            base['src'] = linesrc+'\n'
         elif numOfRecursiveCalls==1:
            recursion = parseRecursion(line)
            if recursion==None:
               sys.exit(0)
            #sanity check
            assert recursion['name']==type['name'],'ERROR: function '+name+' mismatch with:\n>>\t'+line.strip()
            recursion['src'] = linesrc+'\n'
   rewritten = rewriteCode(type,base,recursion,useScan,optimizeConstants)
   return rewritten

prologue = '''
import Control.Parallel.Strategies
import Control.Parallel
import Data.List

parFoldr1 _ [x] = x
parFoldr1 mappend xs  = (ys `par` zs) `pseq` (ys `mappend` zs) where
  len = length xs
  (ys', zs') = splitAt (len `div` 2) xs
  ys = parFoldr1 mappend ys'
  zs = parFoldr1 mappend zs'

'''

def parallelizeFile(filename,useScan=True,optimizeConstants=True):
   name = None
   type = None
   base = None
   recursion = None

   functions = {}

   cachedFoldr1 = getFoldr1()
   setFoldr1('parFoldr1')

   rewritten = prologue

   f = open(filename)
   for linesrc in f:
      line = linesrc.strip()
      if len(line)==0:
         rewritten += linesrc
         continue
      #assert (not hasUnsupportedConstructions(line)), 'ERROR: Unsupported construction:\n'+line.strip()
      if hasUnsupportedConstructions(line):
         if name!=None and name in functions.keys():
            if functions[name]['type']:
               rewritten += functions[name]['type']['src']
            if functions[name]['base']:
               rewritten += functions[name]['base']['src']
            name = None
         rewritten += linesrc
         continue
      if '::' in line and '->' in line:
         type = parseTypeDef(line)

         #assert type!=None,'ERROR: Error while parsing type definition'
         if type==None:
            if name!=None and name in functions.keys():
               if functions[name]['type']:
                  rewritten += functions[name]['type']['src']
               if functions[name]['base']:
                  rewritten += functions[name]['base']['src']
            name = None
            rewritten += linesrc
            continue

         if (name!=None) and name in functions.keys():
            if functions[name]['type']:
               rewritten += functions[name]['type']['src']
            if functions[name]['base']:
               rewritten += functions[name]['base']['src']
            name = None
         name = type['name']
         #assert (type['domain'] in supportedTypes), 'ERROR: unsupported domain type: '+str(type['domain'])+'. Types expected:'+str(supportedTypes)
         if type['domain'] not in supportedTypes:
            rewritten += linesrc
            name = None
            continue
         type['src'] = linesrc
         functions[name] = {'type':type,'base':None,'recursion':None}
         #rewritten += linesrc
      elif '=' in line:
         left = line.split('=')[0].strip()
         right = line.split('=')[1].strip()
         if not name:
            name = left.strip().split()[0].strip()
         #assert type!=None,'ERROR: Type for function '+name+' not defined. Type inference not supported yet.'
         #assert line.strip().split()[0]==name,'ERROR: function '+name+' mismatch with:\n>>\t'+line.strip()
         if name not in functions.keys():
            rewritten += linesrc
            name = None
            continue
         numOfRecursiveCalls = countRecursiveCalls(name, right)
         #assert numOfRecursiveCalls<2,'ERROR: Multiple recursive calls to function '+name+'\n'+line.strip()
         if numOfRecursiveCalls==0:
            base = parseRecursiveBase(line)
            #assert base!=None,'ERROR: Error while parsing base definition'
            if base==None:
               if name!=None and name in functions[name].keys():
                  if functions[name]['type']:
                     rewritten += functions[name]['type']['src']
                  if functions[name]['base']:
                     rewritten += functions[name]['base']['src']
               rewritten += linesrc
               name = None
               continue
            #sanity check
            #assert base['name']==type['name'],'ERROR: function '+name+' mismatch with:\n>>\t'+line.strip()
            if base['name'] not in functions.keys():
               rewritten += linesrc
               name = None
               continue
            base['src'] = linesrc
            functions[base['name']]['base'] = base
         elif numOfRecursiveCalls==1:
            recursion = parseRecursion(line)
            if recursion==None:
               if functions[name]['type']:
                  rewritten += functions[name]['type']['src']
               if functions[name]['base']:
                  rewritten += functions[name]['base']['src']
               rewritten += linesrc
               name = None
               continue
            #sanity check
            #assert recursion['name']==type['name'],'ERROR: function '+name+' mismatch with:\n>>\t'+line.strip()
            if recursion['name'] not in functions.keys():
               if functions[name]['type']:
                  rewritten += functions[name]['type']['src']
               if functions[name]['base']:
                  rewritten += functions[name]['base']['src']
               rewritten += linesrc
               name = None
               continue
            recursion['src'] = linesrc
            functions[recursion['name']]['recursion'] = recursion
            name = recursion['name']
            rewrittenRecursion = None
            if functions[name]['type'] and functions[name]['base']:
               rewrittenRecursion = rewriteCode(functions[name]['type'],functions[name]['base'],functions[name]['recursion'],useScan,optimizeConstants)
            if rewrittenRecursion:
               rewritten += rewrittenRecursion
               name = None
            else:
               if functions[name]['type']:
                  rewritten += functions[name]['type']['src']
               if functions[name]['base']:
                  rewritten += functions[name]['base']['src']
               rewritten += linesrc
               del functions[name]
               name = None
               continue
         else:
            if name!=None and name in functions[name].keys():
               if functions[name]['type']:
                  rewritten += functions[name]['type']['src']
               if functions[name]['base']:
                  rewritten += functions[name]['base']['src']
            rewritten += linesrc

   setFoldr1(cachedFoldr1)
   f.close()

   return rewritten


