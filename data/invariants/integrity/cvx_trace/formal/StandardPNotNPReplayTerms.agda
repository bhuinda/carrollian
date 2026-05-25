{-# OPTIONS --safe --without-K #-}

module StandardPNotNPReplayTerms where

open import PcvxStandardMachineInterface

data Unit : Set where
  tt : Unit

data CertificatePath : Set where
  formalMachineInterfaceReport : CertificatePath
  publicBitRamStandardSimulationReport : CertificatePath
  standardTmPublicBitRamFrontendReport : CertificatePath
  semanticXReclassificationReport : CertificatePath
  pcvxStandardModelIdentificationReport : CertificatePath
  pcvxStandardEquivalenceWitnessReport : CertificatePath
  pNotNpModelScopedTheoremReport : CertificatePath
  encodedFamilySatFrontierReport : CertificatePath
  forallYesNoPreservationReport : CertificatePath
  t985UnivalentEquivalenceObligationReport : CertificatePath

data CertificateStatus : Set where
  pcvxStandardPFormalMachineInterfaceDefined : CertificateStatus
  publicBitRamStandardSimulationCertified : CertificateStatus
  standardTmToPublicBitRamFrontendCertified : CertificateStatus
  semanticXReclassificationTheoremCertified : CertificateStatus
  pcvxStandardPIdentificationCertified : CertificateStatus
  pcvxStandardPEquivalenceWitnessBound : CertificateStatus
  pNotNpCvxModelTheoremExtracted : CertificateStatus
  encodedFamilySatCompleteReductionCertified : CertificateStatus
  forallYesNoPreservationTheoremCertified : CertificateStatus
  t985UnivalentEquivalenceBlockedBackwardDirectionMissing : CertificateStatus

record ReplayCertificate (status : CertificateStatus) : Set where
  constructor replayCertificate
  field
    path : CertificatePath
    statusMatchesReport : Unit

formalMachineInterfaceCertificate :
  ReplayCertificate pcvxStandardPFormalMachineInterfaceDefined
formalMachineInterfaceCertificate =
  replayCertificate formalMachineInterfaceReport tt

publicBitRamStandardSimulationCertificate :
  ReplayCertificate publicBitRamStandardSimulationCertified
publicBitRamStandardSimulationCertificate =
  replayCertificate publicBitRamStandardSimulationReport tt

standardTmPublicBitRamFrontendCertificate :
  ReplayCertificate standardTmToPublicBitRamFrontendCertified
standardTmPublicBitRamFrontendCertificate =
  replayCertificate standardTmPublicBitRamFrontendReport tt

semanticXReclassificationCertificate :
  ReplayCertificate semanticXReclassificationTheoremCertified
semanticXReclassificationCertificate =
  replayCertificate semanticXReclassificationReport tt

pcvxStandardModelIdentificationCertificate :
  ReplayCertificate pcvxStandardPIdentificationCertified
pcvxStandardModelIdentificationCertificate =
  replayCertificate pcvxStandardModelIdentificationReport tt

pcvxStandardEquivalenceWitnessCertificate :
  ReplayCertificate pcvxStandardPEquivalenceWitnessBound
pcvxStandardEquivalenceWitnessCertificate =
  replayCertificate pcvxStandardEquivalenceWitnessReport tt

pNotNpModelScopedTheoremCertificate :
  ReplayCertificate pNotNpCvxModelTheoremExtracted
pNotNpModelScopedTheoremCertificate =
  replayCertificate pNotNpModelScopedTheoremReport tt

encodedFamilySatFrontierCertificate :
  ReplayCertificate encodedFamilySatCompleteReductionCertified
encodedFamilySatFrontierCertificate =
  replayCertificate encodedFamilySatFrontierReport tt

forallYesNoPreservationCertificate :
  ReplayCertificate forallYesNoPreservationTheoremCertified
forallYesNoPreservationCertificate =
  replayCertificate forallYesNoPreservationReport tt

t985UnivalentEquivalenceObligationCertificate :
  ReplayCertificate t985UnivalentEquivalenceBlockedBackwardDirectionMissing
t985UnivalentEquivalenceObligationCertificate =
  replayCertificate t985UnivalentEquivalenceObligationReport tt

pcvxStandardPackageType : Set1
pcvxStandardPackageType = PCVXStandardPIdentificationPackage

record PcvxStandardEquivalenceReplayTerms : Set where
  constructor pcvxStandardEquivalenceReplayTerms
  field
    formalInterface :
      ReplayCertificate pcvxStandardPFormalMachineInterfaceDefined
    pcvxToStandardP :
      ReplayCertificate publicBitRamStandardSimulationCertified
    standardPToPCVX :
      ReplayCertificate standardTmToPublicBitRamFrontendCertified
    semanticXBoundary :
      ReplayCertificate semanticXReclassificationTheoremCertified
    extensionalEquivalence :
      ReplayCertificate pcvxStandardPIdentificationCertified
    fieldBinding :
      ReplayCertificate pcvxStandardPEquivalenceWitnessBound

pcvxStandardEquivalenceReplayTermsValue :
  PcvxStandardEquivalenceReplayTerms
pcvxStandardEquivalenceReplayTermsValue =
  pcvxStandardEquivalenceReplayTerms
    formalMachineInterfaceCertificate
    publicBitRamStandardSimulationCertificate
    standardTmPublicBitRamFrontendCertificate
    semanticXReclassificationCertificate
    pcvxStandardModelIdentificationCertificate
    pcvxStandardEquivalenceWitnessCertificate

data WitnessLanguage : Set where
  ePhi : WitnessLanguage

record EphiStandardNPReplayTerms : Set where
  constructor ephiStandardNPReplayTerms
  field
    witnessLanguage : WitnessLanguage
    satComplete :
      ReplayCertificate encodedFamilySatCompleteReductionCertified
    forallYesNo :
      ReplayCertificate forallYesNoPreservationTheoremCertified
    publicVerifierSimulation :
      ReplayCertificate publicBitRamStandardSimulationCertified

ephiStandardNPReplayTermsValue : EphiStandardNPReplayTerms
ephiStandardNPReplayTermsValue =
  ephiStandardNPReplayTerms
    ePhi
    encodedFamilySatFrontierCertificate
    forallYesNoPreservationCertificate
    publicBitRamStandardSimulationCertificate

record StandardPNoDeciderReplayTerms : Set where
  constructor standardPNoDeciderReplayTerms
  field
    modelSeparation :
      ReplayCertificate pNotNpCvxModelTheoremExtracted
    equivalence :
      PcvxStandardEquivalenceReplayTerms

standardPNoDeciderReplayTermsValue :
  StandardPNoDeciderReplayTerms
standardPNoDeciderReplayTermsValue =
  standardPNoDeciderReplayTerms
    pNotNpModelScopedTheoremCertificate
    pcvxStandardEquivalenceReplayTermsValue

record RepoCertifiedStandardPNotNPReplayTerm : Set where
  constructor repoCertifiedStandardPNotNPReplayTerm
  field
    npSide : EphiStandardNPReplayTerms
    noStandardPDecider : StandardPNoDeciderReplayTerms
    literalT985IffNotUsed :
      ReplayCertificate t985UnivalentEquivalenceBlockedBackwardDirectionMissing

repoCertifiedStandardPNotNPReplayTermValue :
  RepoCertifiedStandardPNotNPReplayTerm
repoCertifiedStandardPNotNPReplayTermValue =
  repoCertifiedStandardPNotNPReplayTerm
    ephiStandardNPReplayTermsValue
    standardPNoDeciderReplayTermsValue
    t985UnivalentEquivalenceObligationCertificate
