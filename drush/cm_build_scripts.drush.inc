<?php

/**
 *  Implements hook_drush_command().
 */
function cm_build_scripts_drush_command() {
  $items = array();
  
  $items['cm-build-scripts-list-servers'] = array(
    'description' => 'Lists Aegir servers',
    'bootstrap' =>  DRUSH_BOOTSTRAP_DRUPAL_FULL,
  );
  
  return $items;
}

/**
 *  Implements drush_command_hook_validate().
 */
function drush_cm_build_scripts_list_servers_validate($service = '') {
  if (!empty($service)) {
    return drush_set_error('CM_BUILD_SCRIPTS_SERVICE_NOT_SPECIFIED');
  }
}

/**
 *  Implements drush_command_hook().
 */
function drush_cm_build_scripts_list_servers($service) {
  $servers = hosting_get_servers($service);
  foreach ($servers as $nid => $title) {
    drush_print($nid . '|' . $title);
  }
}