{-# OPTIONS --cubical --safe --guardedness #-}

module C2SelectorFoundation where

open import Cubical.Foundations.Prelude
open import Cubical.Data.Nat using (ℕ)

record BridgeCounts : Set where
  constructor bridgeCounts
  field
    rawMaskCount : ℕ
    quotientStateCount : ℕ
    nontrivialC2PathPairs : ℕ
    fixedC2Paths : ℕ
    dynamicsCount : ℕ
    selectorCount : ℕ
    contractibleSelectorFibers : ℕ
    noncontractibleSelectorFibers : ℕ

certifiedBridgeCounts : BridgeCounts
certifiedBridgeCounts = bridgeCounts 1023 543 480 63 543 8 5 3

data Selector : Set where
  primitiveSeeded : Selector
  globalActionMinimal : Selector
  pairedActionMinimal : Selector
  rawComponentwiseAbsoluteSpectralGap : Selector
  lazyComponentwiseSpectralGap : Selector
  lazyComponentwiseSpectralGapActionTiebreak : Selector
  pairedLazyComponentwiseSpectralGap : Selector
  pairedLazyComponentwiseSpectralGapActionTiebreak : Selector

record DynamicsCode : Set where
  constructor dynamicsCode
  field
    moveOrbitId : ℕ
    moveOrbitSize : ℕ
    totalMoveAction : ℕ
    rank : ℕ
    nullity : ℕ

primitiveSeededDynamics : DynamicsCode
primitiveSeededDynamics = dynamicsCode 3 2 4795392 288 255

leastActionDynamics : DynamicsCode
leastActionDynamics = dynamicsCode 173 1 1443840 543 0

pairedLeastActionDynamics : DynamicsCode
pairedLeastActionDynamics = dynamicsCode 130 2 2343936 288 255

data SelectedDynamics : Selector → Set where
  primitiveSelected :
    SelectedDynamics primitiveSeeded
  leastActionSelected :
    SelectedDynamics globalActionMinimal
  pairedLeastActionSelected :
    SelectedDynamics pairedActionMinimal
  rawGapSelected :
    DynamicsCode → SelectedDynamics rawComponentwiseAbsoluteSpectralGap
  lazyGapSelected :
    DynamicsCode → SelectedDynamics lazyComponentwiseSpectralGap
  lazyGapActionTiebreakSelected :
    SelectedDynamics lazyComponentwiseSpectralGapActionTiebreak
  pairedLazyGapSelected :
    DynamicsCode → SelectedDynamics pairedLazyComponentwiseSpectralGap
  pairedLazyGapActionTiebreakSelected :
    SelectedDynamics pairedLazyComponentwiseSpectralGapActionTiebreak

primitiveFiberIsContr :
  isContr (SelectedDynamics primitiveSeeded)
primitiveFiberIsContr =
  primitiveSelected , λ { primitiveSelected → refl }

leastActionFiberIsContr :
  isContr (SelectedDynamics globalActionMinimal)
leastActionFiberIsContr =
  leastActionSelected , λ { leastActionSelected → refl }

pairedLeastActionFiberIsContr :
  isContr (SelectedDynamics pairedActionMinimal)
pairedLeastActionFiberIsContr =
  pairedLeastActionSelected , λ { pairedLeastActionSelected → refl }

lazyGapActionTiebreakFiberIsContr :
  isContr (SelectedDynamics lazyComponentwiseSpectralGapActionTiebreak)
lazyGapActionTiebreakFiberIsContr =
  lazyGapActionTiebreakSelected ,
    λ { lazyGapActionTiebreakSelected → refl }

pairedLazyGapActionTiebreakFiberIsContr :
  isContr (SelectedDynamics pairedLazyComponentwiseSpectralGapActionTiebreak)
pairedLazyGapActionTiebreakFiberIsContr =
  pairedLazyGapActionTiebreakSelected ,
    λ { pairedLazyGapActionTiebreakSelected → refl }

data C2TargetQuotient (RawTarget : Set) (tau : RawTarget → RawTarget) : Set where
  point :
    RawTarget → C2TargetQuotient RawTarget tau
  tauPath :
    (m : RawTarget) → point m ≡ point (tau m)
  targetSetTrunc :
    isSet (C2TargetQuotient RawTarget tau)

c2TargetQuotientIsSet :
  {RawTarget : Set} {tau : RawTarget → RawTarget} →
  isSet (C2TargetQuotient RawTarget tau)
c2TargetQuotientIsSet = targetSetTrunc

record WardBalancedDynamicsStructure : Set1 where
  constructor wardBalancedDynamicsStructure
  field
    code : DynamicsCode
    symmetricMarkovOperator : Set
    stationaryWardBmsBalance : Set
    heightCancelsR33Residual : Set

record SkeletalIdentityRule (A : Set) : Set1 where
  field
    StructureCode : Set
    code : A → StructureCode
    codeEqualityToPath : (x y : A) → code x ≡ code y → x ≡ y

record C2SelectorFoundationSkeleton : Set1 where
  field
    RawTarget : Set
    tau : RawTarget → RawTarget
    targetSet : isSet (C2TargetQuotient RawTarget tau)
    dynamicsIdentity : SkeletalIdentityRule DynamicsCode
    selectorFiber : Selector → Set
    primitiveFiberContractible :
      isContr (selectorFiber primitiveSeeded)
    leastActionFiberContractible :
      isContr (selectorFiber globalActionMinimal)
    pairedLeastActionFiberContractible :
      isContr (selectorFiber pairedActionMinimal)
    lazyGapActionTiebreakFiberContractible :
      isContr (selectorFiber lazyComponentwiseSpectralGapActionTiebreak)
    pairedLazyGapActionTiebreakFiberContractible :
      isContr (selectorFiber pairedLazyComponentwiseSpectralGapActionTiebreak)

record ConstructiveUnivalenceGate : Set1 where
  constructor constructiveUnivalenceGate
  field
    equivalenceWitness : Set
    zeroTransportResidue : Set
    heightCoherence : Set
    cubicalSkeletonTypechecks : Set

record CandidateBoundary : Set1 where
  constructor candidateBoundary
  field
    finiteSkeletalCandidate : Set
    notYetFullUnivalenceProof : Set
    nextTargetCubicalFormalization : Set
