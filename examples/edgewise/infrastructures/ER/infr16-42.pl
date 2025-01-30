bwTh(3).
hwTh(1).

node(n1, [ubuntu, mySQL, gcc], (x86, 800), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam11, water]).
node(n15, [ubuntu], (x86, 352), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n4, [gcc, python], (x86, 352), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [arViewer, cam12]).
node(n2, [python, gcc, ubuntu], (arm64, 608), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [heat, echoDot]).
node(n10, [js, ubuntu, mySQL], (arm64, 160), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [nutrient, energy]).
node(n13, [mySQL], (arm64, 384), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n5, [ubuntu, python, js, gcc], (x86, 352), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [piCamera1, piCamera2]).
node(n0, [ubuntu, mySQL], (x86, 448), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [cam22, iphoneXS]).
node(n14, [ubuntu, mySQL, python, js, gcc], (arm64, 352), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n3, [ubuntu, mySQL, python, js, gcc], (x86, 544), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n8, [mySQL, js, gcc], (x86, 544), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam21]).
node(n6, [ubuntu, mySQL, python, js, gcc], (x86, 256), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n9, [ubuntu, mySQL, python, js, gcc], (arm64, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n11, [js, ubuntu], (arm64, 832), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n12, [gcc, python, ubuntu], (arm64, 672), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n7, [mySQL, js], (arm64, 704), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [soil]).

link(n1, n2, 18.0, 313).
link(n2, n1, 18.0, 313).
link(n5, n8, 16, 213).
link(n8, n5, 16, 213).
link(n2, n14, 18.0, 379).
link(n14, n2, 18.0, 379).
link(n6, n11, 21.0, 323).
link(n11, n6, 21.0, 323).
link(n8, n13, 16.0, 275).
link(n13, n8, 16.0, 275).
link(n5, n12, 23.0, 118).
link(n12, n5, 23.0, 118).
link(n10, n14, 12.0, 469).
link(n14, n10, 12.0, 469).
link(n9, n12, 28.0, 299).
link(n12, n9, 28.0, 299).
link(n6, n14, 13.0, 307).
link(n14, n6, 13.0, 307).
link(n2, n5, 26.0, 118).
link(n5, n2, 26.0, 118).
link(n0, n6, 10.0, 472).
link(n6, n0, 10.0, 472).
link(n8, n11, 13, 23).
link(n11, n8, 13, 23).
link(n2, n11, 14.0, 386).
link(n11, n2, 14.0, 386).
link(n5, n10, 20.0, 249).
link(n10, n5, 20.0, 249).
link(n5, n9, 37.0, 154).
link(n9, n5, 37.0, 154).
link(n7, n15, 33.0, 58).
link(n15, n7, 33.0, 58).
link(n0, n13, 14, 207).
link(n13, n0, 14, 207).
link(n8, n9, 21.0, 147).
link(n9, n8, 21.0, 147).
link(n9, n15, 12.0, 189).
link(n15, n9, 12.0, 189).
link(n3, n13, 17.0, 272).
link(n13, n3, 17.0, 272).
link(n3, n7, 19.0, 132).
link(n7, n3, 19.0, 132).
link(n11, n13, 29.0, 37).
link(n13, n11, 29.0, 37).
link(n9, n14, 30.0, 170).
link(n14, n9, 30.0, 170).
link(n1, n9, 33.0, 323).
link(n9, n1, 33.0, 323).
link(n2, n8, 10.0, 403).
link(n8, n2, 10.0, 403).
link(n0, n2, 8, 274).
link(n2, n0, 8, 274).
link(n10, n15, 20.0, 266).
link(n15, n10, 20.0, 266).
link(n2, n15, 10, 436).
link(n15, n2, 10, 436).
link(n0, n10, 2, 394).
link(n10, n0, 2, 394).
link(n14, n14, 0.0, inf).
link(n10, n12, 3, 368).
link(n12, n10, 3, 368).
link(n3, n3, 0.0, inf).
link(n6, n8, 8.0, 329).
link(n8, n6, 8.0, 329).
link(n12, n14, 15.0, 174).
link(n14, n12, 15.0, 174).
link(n11, n11, 0.0, inf).
link(n1, n4, 32.0, 436).
link(n4, n1, 32.0, 436).
link(n1, n11, 25.0, 303).
link(n11, n1, 25.0, 303).
link(n5, n7, 33.0, 439).
link(n7, n5, 33.0, 439).
link(n1, n12, 11.0, 496).
link(n12, n1, 11.0, 496).
link(n0, n1, 10.0, 145).
link(n1, n0, 10.0, 145).
link(n2, n13, 22.0, 210).
link(n13, n2, 22.0, 210).
link(n1, n8, 12.0, 421).
link(n8, n1, 12.0, 421).
link(n4, n10, 24.0, 57).
link(n10, n4, 24.0, 57).
link(n0, n3, 4.0, 345).
link(n3, n0, 4.0, 345).
link(n9, n13, 37.0, 342).
link(n13, n9, 37.0, 342).
link(n5, n14, 28.0, 133).
link(n14, n5, 28.0, 133).
link(n13, n15, 32.0, 325).
link(n15, n13, 32.0, 325).
link(n15, n15, 0.0, inf).
link(n10, n13, 15.0, 147).
link(n13, n10, 15.0, 147).
link(n1, n15, 27.0, 123).
link(n15, n1, 27.0, 123).
link(n6, n6, 0.0, inf).
link(n4, n4, 0.0, inf).
link(n9, n9, 0.0, inf).
link(n0, n9, 23.0, 296).
link(n9, n0, 23.0, 296).
link(n6, n12, 15.0, 399).
link(n12, n6, 15.0, 399).
link(n2, n7, 23.0, 94).
link(n7, n2, 23.0, 94).
link(n8, n12, 7.0, 56).
link(n12, n8, 7.0, 56).
link(n2, n3, 12.0, 368).
link(n3, n2, 12.0, 368).
link(n2, n6, 18.0, 179).
link(n6, n2, 18.0, 179).
link(n2, n9, 22.0, 423).
link(n9, n2, 22.0, 423).
link(n1, n5, 28.0, 317).
link(n5, n1, 28.0, 317).
link(n5, n15, 33.0, 265).
link(n15, n5, 33.0, 265).
link(n5, n11, 29.0, 336).
link(n11, n5, 29.0, 336).
link(n5, n6, 24.0, 118).
link(n6, n5, 24.0, 118).
link(n5, n5, 0.0, inf).
link(n6, n13, 11.0, 490).
link(n13, n6, 11.0, 490).
link(n9, n10, 25.0, 283).
link(n10, n9, 25.0, 283).
link(n1, n13, 7, 135).
link(n13, n1, 7, 135).
link(n3, n14, 14.0, 193).
link(n14, n3, 14.0, 193).
link(n13, n13, 0.0, inf).
link(n5, n13, 32.0, 435).
link(n13, n5, 32.0, 435).
link(n1, n10, 8, 41).
link(n10, n1, 8, 41).
link(n4, n12, 21.0, 25).
link(n12, n4, 21.0, 25).
link(n12, n13, 18.0, 300).
link(n13, n12, 18.0, 300).
link(n4, n14, 29.0, 299).
link(n14, n4, 29.0, 299).
link(n7, n8, 17.0, 182).
link(n8, n7, 17.0, 182).
link(n4, n9, 13, 411).
link(n9, n4, 13, 411).
link(n4, n6, 36.0, 252).
link(n6, n4, 36.0, 252).
link(n14, n15, 18, 428).
link(n15, n14, 18, 428).
link(n6, n7, 25.0, 441).
link(n7, n6, 25.0, 441).
link(n3, n5, 18.0, 282).
link(n5, n3, 18.0, 282).
link(n2, n4, 34.0, 443).
link(n4, n2, 34.0, 443).
link(n6, n9, 29.0, 214).
link(n9, n6, 29.0, 214).
link(n6, n15, 25.0, 195).
link(n15, n6, 25.0, 195).
link(n0, n0, 0.0, inf).
link(n0, n11, 15.0, 116).
link(n11, n0, 15.0, 116).
link(n0, n8, 2, 368).
link(n8, n0, 2, 368).
link(n1, n7, 21.0, 135).
link(n7, n1, 21.0, 135).
link(n4, n7, 11, 475).
link(n7, n4, 11, 475).
link(n10, n10, 0.0, inf).
link(n11, n15, 4, 45).
link(n15, n11, 4, 45).
link(n7, n10, 13.0, 70).
link(n10, n7, 13.0, 70).
link(n12, n15, 23.0, 374).
link(n15, n12, 23.0, 374).
link(n1, n1, 0.0, inf).
link(n1, n3, 10.0, 483).
link(n3, n1, 10.0, 483).
link(n1, n14, 9, 342).
link(n14, n1, 9, 342).
link(n0, n12, 5.0, 177).
link(n12, n0, 5.0, 177).
link(n0, n15, 18.0, 292).
link(n15, n0, 18.0, 292).
link(n11, n12, 20.0, 321).
link(n12, n11, 20.0, 321).
link(n2, n10, 10.0, 257).
link(n10, n2, 10.0, 257).
link(n3, n12, 9.0, 392).
link(n12, n3, 9.0, 392).
link(n7, n14, 18, 450).
link(n14, n7, 18, 450).
link(n3, n4, 30.0, 147).
link(n4, n3, 30.0, 147).
link(n7, n9, 24.0, 420).
link(n9, n7, 24.0, 420).
link(n7, n11, 30.0, 166).
link(n11, n7, 30.0, 166).
link(n0, n5, 18.0, 497).
link(n5, n0, 18.0, 497).
link(n4, n13, 29.0, 488).
link(n13, n4, 29.0, 488).
link(n8, n10, 4.0, 457).
link(n10, n8, 4.0, 457).
link(n0, n4, 26.0, 327).
link(n4, n0, 26.0, 327).
link(n9, n11, 8, 54).
link(n11, n9, 8, 54).
link(n8, n15, 17.0, 496).
link(n15, n8, 17.0, 496).
link(n10, n11, 17.0, 211).
link(n11, n10, 17.0, 211).
link(n3, n10, 6.0, 177).
link(n10, n3, 6.0, 177).
link(n0, n7, 15.0, 427).
link(n7, n0, 15.0, 427).
link(n7, n12, 10, 252).
link(n12, n7, 10, 252).
link(n8, n8, 0.0, inf).
link(n4, n5, 44.0, 271).
link(n5, n4, 44.0, 271).
link(n8, n14, 12.0, 361).
link(n14, n8, 12.0, 361).
link(n3, n11, 15.0, 467).
link(n11, n3, 15.0, 467).
link(n0, n14, 10, 77).
link(n14, n0, 10, 77).
link(n4, n15, 25.0, 318).
link(n15, n4, 25.0, 318).
link(n2, n12, 13.0, 65).
link(n12, n2, 13.0, 65).
link(n3, n9, 23.0, 403).
link(n9, n3, 23.0, 403).
link(n3, n6, 6, 28).
link(n6, n3, 6, 28).
link(n13, n14, 16.0, 405).
link(n14, n13, 16.0, 405).
link(n12, n12, 0.0, inf).
link(n3, n15, 19.0, 412).
link(n15, n3, 19.0, 412).
link(n1, n6, 4, 56).
link(n6, n1, 4, 56).
link(n11, n14, 22.0, 146).
link(n14, n11, 22.0, 146).
link(n4, n8, 28.0, 357).
link(n8, n4, 28.0, 357).
link(n3, n8, 2, 385).
link(n8, n3, 2, 385).
link(n6, n10, 12.0, 384).
link(n10, n6, 12.0, 384).
link(n2, n2, 0.0, inf).
link(n4, n11, 21.0, 472).
link(n11, n4, 21.0, 472).
link(n7, n13, 18, 180).
link(n13, n7, 18, 180).
link(n7, n7, 0.0, inf).

nodeType(n0, edge).
nodeType(n1, edge).
nodeType(n2, thing).
nodeType(n3, cloud).
nodeType(n4, thing).
nodeType(n5, edge).
nodeType(n6, cloud).
nodeType(n7, edge).
nodeType(n8, thing).
nodeType(n9, cloud).
nodeType(n10, thing).
nodeType(n11, edge).
nodeType(n12, edge).
nodeType(n13, thing).
nodeType(n14, cloud).
nodeType(n15, thing).

location(n0, de).
location(n1, es).
location(n2, de).
location(n3, it).
location(n4, it).
location(n5, es).
location(n6, de).
location(n7, es).
location(n8, de).
location(n9, es).
location(n10, es).
location(n11, es).
location(n12, it).
location(n13, de).
location(n14, it).
location(n15, de).

provider(n0, aws).
provider(n1, ibm).
provider(n2, aws).
provider(n3, ibm).
provider(n4, ibm).
provider(n5, aws).
provider(n6, aws).
provider(n7, aws).
provider(n8, ibm).
provider(n9, aws).
provider(n10, aws).
provider(n11, ibm).
provider(n12, ibm).
provider(n13, azure).
provider(n14, azure).
provider(n15, azure).
