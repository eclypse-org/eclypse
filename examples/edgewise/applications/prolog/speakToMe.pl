% service(ServiceId, SWReqs, (Arch, HWReqs)).
service(storage, [ubuntu], (x86, 100)).
service(database, [mySQL, ubuntu], (x86, 50)).
service(queue, [python], (x86, 2)).
service(tts, [python, gcc], (arm64, 4)).

% function(FunctionId, SWPlatform, (Arch, HWReqs)).
function(uploadFun, python, (x86, 20)).
function(metadataFun, python, (arm64, 2)).
function(publishFun, js, (x86, 4)).
function(ttsFun, python, (arm64, 30)).

% thing(ThingId, TType).
thing(smph, smartphone).
thing(spk, speaker).


% --- APPLICATION ---
% application(AppId, [Functions], [Services]).
application(speakToMe, [uploadPost,metaPost,publishPost,convertTxt,uploadAudio,metaAudio], [textBucket,audioBucket,mainDB,postQueue,converter]).

% serviceInstance(SIId, ServiceId).
serviceInstance(textBucket, storage).
serviceInstance(audioBucket, storage).
serviceInstance(mainDB, database).
serviceInstance(postQueue, queue).
serviceInstance(converter, tts).

% functionInstance(FIId, FunctionId, (ReqXMonth, ReqDuration)).
functionInstance(uploadPost, uploadFun, (1000, 30)).
functionInstance(metaPost, metadataFun, (1500, 8)).
functionInstance(publishPost, publishFun, (2000, 8)).
functionInstance(convertTxt, ttsFun, (2500, 30)).
functionInstance(uploadAudio, uploadFun, (1000, 20)).
functionInstance(metaAudio, metadataFun, (2500, 130)).

% thingInstance(TIId, ThingId).
thingInstance(iphoneXS, smph).
thingInstance(echoDot, spk).

% dataFlow(Source, Dest, DataId, SecReqs, Size, Rate, MaxLat).
dataFlow(iphoneXS, uploadPost, post, [enc_iot, authentication, firewall], 0.4, 5, 60).
dataFlow(uploadPost, textBucket, post, [authentication, enc_storage], 0.4, 5, 80).
dataFlow(textBucket, metaPost, post, [public_key_crypto], 0.4, 6, 40).
dataFlow(metaPost, mainDB, meta, [anti_tampering, enc_storage], 0.1, 6, 30).
dataFlow(textBucket, publishPost, post, [anti_tampering], 0.4, 5, 60).
dataFlow(publishPost, postQueue, post, [access_logs, enc_storage], 0.2, 5, 50).
dataFlow(postQueue, convertTxt, post, [access_logs, enc_storage], 0.2, 8, 40).
dataFlow(convertTxt, converter, post, [anti_tampering, access_logs], 0.2, 8, 40).
dataFlow(converter, convertTxt, speech, [anti_tampering, access_logs], 0.2, 8, 30).
dataFlow(convertTxt, echoDot, speech, [enc_iot, access_logs, public_key_crypto], 0.5, 8, 30).
dataFlow(convertTxt, metaAudio, speech, [authentication, enc_storage], 0.5, 8, 70).
dataFlow(metaAudio, mainDB, meta, [anti_tampering, enc_storage], 0.1, 10, 20).
dataFlow(convertTxt, uploadAudio, speech, [node_isolation, access_control], 0.8, 8, 30).
dataFlow(uploadAudio, audioBucket, speech, [authentication, enc_storage], 0.8, 8, 40).