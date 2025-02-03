%:-['../../pl-utils/costs.pl', '../../pl-utils/requirements.pl'].
% :-['/Users/jacopomassa/GitHub/eclypse/examples/edgewise/infrastructures/BA/infr128-3997.pl'].
% :-['/Users/jacopomassa/GitHub/eclypse/examples/edgewise/applications/prolog/speakToMe.pl'].
% :-['/Users/jacopomassa/GitHub/eclypse/examples/edgewise/pl-utils/requirements.pl'].
% :-['/Users/jacopomassa/GitHub/eclypse/examples/edgewise/pl-utils/costs.pl'].
:- ['comp.pl'].
:- ['../../pl-utils/requirements.pl', '../../pl-utils/costs.pl'].

:- set_prolog_flag(answer_write_options,[max_depth(0)]). % write answers' text entirely
:- set_prolog_flag(stack_limit, 32 000 000 000).
:- set_prolog_flag(last_call_optimisation, true).

:- dynamic deployed/2.

stats(App, Placement, Cost, Bins, Infs, Time) :-
    statistics(inferences, InfA),
        statistics(cputime, TimeA),
            best(App, Placement, Cost),
            countDistinct(Placement, Bins),
        statistics(cputime, TimeB),
    statistics(inferences, InfB),

    Infs is InfB - InfA,
    Time is TimeB - TimeA.

best(App, Placement, Cost) :-
    \+ deployed(App, _),
    application(App, Functions, Services),
    checkThings, 
    ranking(Functions, Services, RankedComps),
    findCompatibles(RankedComps, Components),
    findBudget(Components, Budget),
    placement(Components, Placement, Budget, Cost),
    qosOK(Placement).
best(App, Placement, Cost) :-
    deployed(App, OldPlacement),
    crStep(OldPlacement, Compatibles),
    findBudget(Compatibles, Budget),
    placement(Compatibles, Placement, Budget, Cost),
    qosOK(Placement).

crStep(P, Compatibles) :- crStep(P, [], Compatibles).
crStep([(C,N)|P], POk, [(C,[(Cost,H,N)])|Cs]) :-
    compComponentPlacement(C, N, P), compQosOK(C, N, POk),
    lightNodeOK(C, N, H, Cost),
    crStep(P, [(C,N)|POk], Cs).
crStep([(C,N)|P], POk, [(C,[Comp|Atibles])|Cs]) :-
    \+ ( compComponentPlacement(C, N, P); compQosOK(C, N, POk) ), 
    findall((N, H, Cost), lightNodeOK(C, N, H, Cost), [Comp|Atibles]),
    crStep(P, POk, Cs).
crStep([], _, []).

findBudget(C, B) :- findBudget(C, 0, B).
findBudget([(_, Comps)|Cs], OldB, NewB) :-
    maxCost(Comps, CB), TmpB is OldB + CB,
    findBudget(Cs, TmpB, NewB).
findBudget([], B, B).

maxCost(Comps, MaxCost) :- member((MaxCost,_,N), Comps), \+ (member((CostM,_,M), Comps), dif(N,M), CostM > MaxCost).

checkThings :-
    findall(T, thingInstance(T, _), Things),
    findall(T, (node(_, _, _, _, IoTCaps), member(T, IoTCaps)), IoT),
    subset(Things, IoT).

countDistinct(P, L) :-
    findall(N, distinct(member((_,N), P)), S),
    sort(S, Ss), length(Ss, L).

findCompatibles(Compatibles, Components) :- findCompatibles(Compatibles, [], Components).
findCompatibles([(_,C)|Cs], OldC, NewC):-
    findall((Cost, H, M), lightNodeOK(C, M, H, Cost), [Comp|Atibles]), 
    sort([Comp|Atibles], SCompatibles), % cannot be empty
    findCompatibles(Cs, [(C,SCompatibles)|OldC], NewC).
findCompatibles([], C, C).

lightNodeOK(S,N,H,SCost) :-
    serviceInstance(S, SId), service(SId, SWReqs, (Arch, HWReqs)),
    node(N, SWCaps, (Arch, HWCaps), _, _),
    requirements(SId, N),
    subset(SWReqs, SWCaps), 
    HWCaps >= HWReqs, H is 1/HWCaps, % H used to sort Compatibles (ascending H --> descending HWCaps)) 
    nodeType(N, Type), cost(Type, S, SCost).

lightNodeOK(F,N,H,FCost) :-
    functionInstance(F, FId, _), function(FId, SWPlatform, (Arch, HWReqs)),
    node(N, SWCaps, (Arch, HWCaps), _, _),
    requirements(FId, N),
    member(SWPlatform, SWCaps), 
    HWCaps >= HWReqs, H is 1/HWCaps,
    nodeType(N, Type), cost(Type, F, FCost).

placement(Cs, Placement, Budget, NewCost) :- placement(Cs, [], Placement, Budget, 0, NewCost).

placement([(C, Comps)|Cs], OldP, NewP, Budget, OldCost, NewCost) :-
    componentPlacement(C, Comps, N, OldP, CCost),
    TCost is OldCost + CCost, TCost =< Budget,
    placement(Cs, [(C,N)|OldP], NewP, Budget, TCost, NewCost).
placement([], P, P, _, Cost, Cost).

componentPlacement(F, Comps, N, Ps, FCost) :-
    functionInstance(F, FId, _), function(FId, _, HWReqs),
    member((_,N), Ps), member((FCost,_,N), Comps),
    compatible(N, HWReqs, Ps).
componentPlacement(F, Comps, N, Ps, FCost) :-
    functionInstance(F, FId, _), function(FId, _, HWReqs),
    member((FCost,_,N), Comps), \+ member((_,N),Ps),
    compatible(N, HWReqs, Ps).

componentPlacement(S, Comps, N, Ps, SCost) :-
    serviceInstance(S, SId), service(SId, _, HWReqs),
    member((_,N), Ps), member((SCost,_,N), Comps),
    compatible(N, HWReqs, Ps).
componentPlacement(S, Comps, N, Ps, SCost) :-
    serviceInstance(S, SId), service(SId, _, HWReqs),
    member((SCost,_,N), Comps), \+ member((_,N),Ps),
    compatible(N, HWReqs, Ps).

compatible(N, (Arch,HWReqs), Ps) :- node(N, _, (Arch, HWCaps), _, _), hwOK(N, HWCaps, HWReqs, Ps).

hwOK(N,HWCaps,HWReqs,Ps) :-
    findall(HW, hwOnN(N, Ps, HW), HWs), sum_list(HWs,TotHW),
    hwTh(T), HWCaps >= TotHW + HWReqs + T.

hwOnN(N, Ps, HW) :- serviceInstance(S, SId), service(SId,_,(_,HW)), member((S,N), Ps).
hwOnN(N, Ps, HW) :- functionInstance(F, FId,_), function(FId,_,(_,HW)), member((F,N), Ps).

qosOK(Ps) :- findall((N1N2, Lat, Sec), relevant(N1N2, Ps, Lat, _, Sec), DataFlows), checkDF(DataFlows, Ps).

checkDF([((N1,N2),ReqLat,SecReqs)|DFs], Ps) :-
    (link(N1, N2, FeatLat, FeatBW); link(N2, N1, FeatLat, FeatBW)),
    secOK(N1, N2, SecReqs),
    FeatLat =< ReqLat, bwOK((N1,N2), FeatBW, Ps),
    checkDF(DFs, Ps).
checkDF([], _).

bwOK(N1N2, FeatBW, Ps):-
    findall(BW, relevant(N1N2, Ps, _, BW, _), BWs), sum_list(BWs, OkAllocBW), 
    bwTh(T), FeatBW >= OkAllocBW + T.

secOK(N1, N2, SecReqs) :-
    node(N1, _, _, SecCaps1, _), subset(SecReqs, SecCaps1),
    node(N2, _, _, SecCaps2, _), subset(SecReqs, SecCaps2).

relevant((N1,N2), Ps, Lat, BW, Sec):-
    dataFlow(T1, T2, _, Sec, Size, Rate, Lat),
    (member((T1,N1), Ps); node(N1, _, _, _, IoTCaps), member(T1, IoTCaps)),
    (member((T2,N2), Ps); node(N2, _, _, _, IoTCaps), member(T2, IoTCaps)),
    BW is Size*Rate.