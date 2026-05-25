{-# OPTIONS --cubical --safe --guardedness #-}

module C2SelectorFoundationSelectorFiniteSubtypeLookupTableSoundness where

open import Cubical.Foundations.Prelude using (_≡_ ; refl)
open import Cubical.Foundations.Equiv using (_≃_)
open import Cubical.Data.Nat using (ℕ ; _+_)
open import Cubical.Data.Fin.Base using (Fin)
open import C2SelectorFoundation
import C2SelectorFoundationSelectorFiniteSubtypeRaw543IndexedLookup as RawLookup
import C2SelectorFoundationSelectorFiniteSubtypeLazy63IndexedLookup as LazyLookup
import C2SelectorFoundationSelectorFiniteSubtypePairedLazy480IndexedLookup as PairedLookup

raw543LookupTableRowCount : ℕ
raw543LookupTableRowCount = 543

lazy63LookupTableRowCount : ℕ
lazy63LookupTableRowCount = 63

pairedLazy480LookupTableRowCount : ℕ
pairedLazy480LookupTableRowCount = 480

lookupTableSelectorCount : ℕ
lookupTableSelectorCount = 3

lookupTableTotalRowCount : ℕ
lookupTableTotalRowCount =
  raw543LookupTableRowCount + lazy63LookupTableRowCount + pairedLazy480LookupTableRowCount

lookupTableTotalRowCountIs1086 : lookupTableTotalRowCount ≡ 1086
lookupTableTotalRowCountIs1086 = refl

raw543LookupTableSoundness :
  RawLookup.SelectorFiber rawComponentwiseAbsoluteSpectralGap ≃ Fin raw543LookupTableRowCount
raw543LookupTableSoundness = RawLookup.rawSpectralGapLookupFiberEquivFin

lazy63LookupTableSoundness :
  LazyLookup.SelectorFiber lazyComponentwiseSpectralGap ≃ Fin lazy63LookupTableRowCount
lazy63LookupTableSoundness = LazyLookup.lazySpectralGapLookupFiberEquivFin

pairedLazy480LookupTableSoundness :
  PairedLookup.SelectorFiber pairedLazyComponentwiseSpectralGap ≃
  Fin pairedLazy480LookupTableRowCount
pairedLazy480LookupTableSoundness = PairedLookup.pairedLazySpectralGapLookupFiberEquivFin
