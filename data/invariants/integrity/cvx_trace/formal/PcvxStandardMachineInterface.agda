{-# OPTIONS --safe --without-K #-}

module PcvxStandardMachineInterface where

data Nat : Set where
  zero : Nat
  suc : Nat -> Nat

data Bool : Set where
  false : Bool
  true : Bool

data List (A : Set) : Set where
  [] : List A
  _::_ : A -> List A -> List A

infix 4 _==_

data _==_ {A : Set} (x : A) : A -> Set where
  refl : x == x

record Sigma (A : Set) (B : A -> Set) : Set where
  constructor pair
  field
    fst : A
    snd : B fst

Language : Set
Language = List Bool -> Bool

record PolyBound : Set where
  constructor poly
  field
    degree : Nat
    coefficient : Nat
    offset : Nat

record StandardMachine : Set1 where
  field
    state : Set
    publicTransitionTable : Set
    standardAccepts : List Bool -> Bool
    standardTimeBound : PolyBound

StandardDecides : StandardMachine -> Language -> Set
StandardDecides machine language =
  (input : List Bool) ->
    StandardMachine.standardAccepts machine input == language input

record StandardPWitness (language : Language) : Set1 where
  field
    machine : StandardMachine
    decides : StandardDecides machine language

StandardP : Language -> Set1
StandardP = StandardPWitness

record StandardNPWitness (language : Language) : Set1 where
  field
    verifier : StandardMachine
    certificate : List Bool -> Set
    verifies : (input : List Bool) -> certificate input -> Set
    sound : (input : List Bool) -> certificate input -> language input == true
    complete : (input : List Bool) -> language input == true -> certificate input

StandardNP : Language -> Set1
StandardNP = StandardNPWitness

data CvxEventKind : Set where
  CPublic : CvxEventKind
  VPublic : CvxEventKind
  XExtractor : CvxEventKind
  Residue : CvxEventKind

data COnlyTrace : List CvxEventKind -> Set where
  cNil : COnlyTrace []
  cCons : {events : List CvxEventKind} -> COnlyTrace events -> COnlyTrace (CPublic :: events)

data NoXTrace : List CvxEventKind -> Set where
  noXNil : NoXTrace []
  noXConsC : {events : List CvxEventKind} -> NoXTrace events -> NoXTrace (CPublic :: events)
  noXConsV : {events : List CvxEventKind} -> NoXTrace events -> NoXTrace (VPublic :: events)

record CvxProgram : Set where
  field
    cvxTraceOn : List Bool -> List CvxEventKind
    cvxAccepts : List Bool -> Bool
    cvxTimeBound : PolyBound
    traceOverheadBound : PolyBound

CvxDecides : CvxProgram -> Language -> Set
CvxDecides program language =
  (input : List Bool) ->
    CvxProgram.cvxAccepts program input == language input

record PCVXWitness (language : Language) : Set where
  field
    program : CvxProgram
    cOnly : (input : List Bool) -> COnlyTrace (CvxProgram.cvxTraceOn program input)
    noX : (input : List Bool) -> NoXTrace (CvxProgram.cvxTraceOn program input)
    decides : CvxDecides program language

P_CVX : Language -> Set
P_CVX = PCVXWitness

record NPCVXWitness (language : Language) : Set1 where
  field
    witnessProgram : CvxProgram
    publicCertificate : List Bool -> Set
    noXVerifierTrace :
      (input : List Bool) ->
      publicCertificate input ->
      NoXTrace (CvxProgram.cvxTraceOn witnessProgram input)
    witnessSound :
      (input : List Bool) ->
      publicCertificate input ->
      language input == true
    witnessComplete :
      (input : List Bool) ->
      language input == true ->
      publicCertificate input

NP_CVX : Language -> Set1
NP_CVX = NPCVXWitness

record ClassEquivalence
  (left : Language -> Set)
  (right : Language -> Set1)
  : Set1 where
  field
    to : (language : Language) -> left language -> right language
    from : (language : Language) -> right language -> left language

PCVXStandardPEquivalence : Set1
PCVXStandardPEquivalence = ClassEquivalence P_CVX StandardP

record SemanticXBoundary : Set1 where
  field
    pureCNoHiddenRecovery : Set
    hiddenRecoveryReclassifiedX : Set
    standardPublicExecutionsAreCOnly : Set

record PCVXStandardPIdentificationPackage : Set1 where
  field
    pcvxToStandardP : (language : Language) -> P_CVX language -> StandardP language
    standardPToPCVX : (language : Language) -> StandardP language -> P_CVX language
    semanticXBoundary : SemanticXBoundary
    extensionalEquivalence : PCVXStandardPEquivalence
