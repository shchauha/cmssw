import FWCore.ParameterSet.Config as cms

# trajetory seeds

import FastSimulation.Tracking.TrajectorySeedProducer_cfi
iterativeInitialSeeds = FastSimulation.Tracking.TrajectorySeedProducer_cfi.trajectorySeedProducer.clone()
iterativeInitialSeeds.simTrackSelection.pTMin = 0.4
iterativeInitialSeeds.simTrackSelection.maxD0 = 1.0
iterativeInitialSeeds.simTrackSelection.maxZ0 = 999
iterativeInitialSeeds.minLayersCrossed = 3
# note: standard tracking uses for originRadius 0.03, but this value 
# gives a much better agreement in rate and shape for iter0
iterativeInitialSeeds.originpTMin = 0.6
iterativeInitialSeeds.originRadius = 1.0 
iterativeInitialSeeds.originHalfLength = 999
iterativeInitialSeeds.primaryVertex = ''

from RecoTracker.TkSeedingLayers.PixelLayerTriplets_cfi import PixelLayerTriplets
iterativeInitialSeeds.layerList = PixelLayerTriplets.layerList

# track candidates

import FastSimulation.Tracking.TrackCandidateProducer_cfi
iterativeInitialTrackCandidates = FastSimulation.Tracking.TrackCandidateProducer_cfi.trackCandidateProducer.clone()
iterativeInitialTrackCandidates.SeedProducer = cms.InputTag("iterativeInitialSeeds")
iterativeInitialTrackCandidates.MinNumberOfCrossedLayers = 3

# tracks

import RecoTracker.TrackProducer.CTFFinalFitWithMaterial_cfi
iterativeInitialTracks = RecoTracker.TrackProducer.CTFFinalFitWithMaterial_cfi.ctfWithMaterialTracks.clone()
iterativeInitialTracks.src = 'iterativeInitialTrackCandidates'
iterativeInitialTracks.TTRHBuilder = 'WithoutRefit'
iterativeInitialTracks.Fitter = 'KFFittingSmootherWithOutlierRejection'
iterativeInitialTracks.Propagator = 'PropagatorWithMaterial'
iterativeInitialTracks.AlgorithmName = cms.string('initialStep')

#vertices
from RecoTracker.IterativeTracking.InitialStep_cff import firstStepPrimaryVertices
firstStepPrimaryVertices.TrackLabel = cms.InputTag("iterativeInitialTracks")

# track identification
# why not import the configurstion from the full initial step?
# and similar for other iterations

import RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi
initialStepSelector = RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.multiTrackSelector.clone(
        src='iterativeInitialTracks',
        trackSelectors= cms.VPSet(
            RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.looseMTS.clone(
                name = 'initialStepLoose',
                            ), 
                    RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.tightMTS.clone(
                name = 'initialStepTight',
                            preFilterName = 'initialStepLoose',
                            ),
                    RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi.highpurityMTS.clone(
                name = 'initialStep',
                            preFilterName = 'initialStepTight',
                            ),
            ) 
        ) 

# simtrack id producer

initialStepIds = cms.EDProducer("SimTrackIdProducer",
                                trackCollection = cms.InputTag("iterativeInitialTracks"),
                                HitProducer = cms.InputTag("siTrackerGaussianSmearingRecHits","TrackerGSMatchedRecHits")
                                )

# final sequence

iterativeInitialStep = cms.Sequence(iterativeInitialSeeds
                                    +iterativeInitialTrackCandidates
                                    +iterativeInitialTracks                                    
                                    +firstStepPrimaryVertices
                                    +initialStepSelector
                                    +initialStepIds)




