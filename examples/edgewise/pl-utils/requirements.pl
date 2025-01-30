% requirements(T,N) effettua
% - location(N, Loc), provider(N, Provider) nodeType(N, Type)
% - policy di sicurezza (SecFog) i.e. audit, antitampering, etc.
% - avg banda entrante/uscente
% - 
% requirements(Type, N)

% --- SERVICES ---
requirements(queue, _).
requirements(tts, _).
requirements(imageRecognition, _).
requirements(imageDetection, _).

requirements(storage, N) :-
    avgInBW(N, 100), avgOutBW(N, 200).

requirements(dashboard, N) :-
    node(N, _, _, SecCaps, _),
    location(N, 'it'),
    member(resource_monitoring, SecCaps),
    member(public_key_crypto, SecCaps),
    member(authentication, SecCaps).

requirements(database, N) :-
    node(N, _, _, SecCaps, _),
    (provider(N, 'aws'); provider(N, 'azure')),
    secure_storage(SecCaps),
    member(access_logs, SecCaps),
    member(network_ids, SecCaps),
    member(authentication, SecCaps),
    avgInBW(N, 200).

% --- FUNCTIONS ---
requirements(uploadFun, _).
requirements(metadataFun, _).
requirements(publishFun, _).
requirements(ttsFun, _).
requirements(camCalibration, _).
requirements(imgRectification, _).
requirements(roiSelection, _).
requirements(vehicleTrajectory, _).
requirements(updateStatus, _).

% --- UTILS---
avg_list(List, Avg) :- length(List, N), sum_list(List, Sum), Avg is Sum / N.

avgInBW(N, ReqInBW) :- findall(BW, (link(M, N, _, BW), dif(N,M)), BWs), avg_list(BWs, AvgInBW), AvgInBW >= ReqInBW.
avgOutBW(N, ReqOutBW) :- findall(BW, (link(N, M, _, BW), dif(N,M)), BWs), avg_list(BWs, AvgOutBW), AvgOutBW >= ReqOutBW.

secure_storage(SecCaps) :- 
    member(backup, SecCaps);
    (member(enc_storage, SecCaps), member(obfuscated_storage, SecCaps)).