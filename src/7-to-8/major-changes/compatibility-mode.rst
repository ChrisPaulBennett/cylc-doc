.. _cylc_7_compat_mode:

Cylc 7 Compatibility Mode
=========================

.. admonition:: Does This Change Affect Me?
   :class: tip

   This will affect you if you want to run Cylc 7 (``suite.rc``) workflows
   using Cylc 8.0

Overview
--------

Cylc 8 can run most Cylc 7 workflows "as is".
The ``suite.rc`` filename triggers a backward compatibility mode in which:

- :term:`implicit tasks <implicit task>` are allowed by default

  - (unless a ``rose-suite.conf`` file is found in the :term:`run directory`
    for consistency with ``rose suite-run`` behaviour)
  - (Cylc 8 does not allow implicit tasks by default)

- :term:`cycle point time zone` defaults to the local time zone

  - (Cylc 8 defaults to UTC)

- waiting tasks are pre-spawned to mimic the Cylc 7 scheduling algorithm and
  stall behaviour, and these require
  :term:`suicide triggers <suicide trigger>`
  for alternate :term:`graph branching`

  - (Cylc 8 spawns tasks on demand, and suicide triggers are not needed for
    branching)

- only ``succeeded`` task outputs are :ref:`*expected* <User Guide Expected Outputs>`,
  meaning the scheduler will retain tasks that do not succeed as incomplete

  - (in Cylc 8, **all** outputs are *expected* unless marked as
    :ref:`*optional* <User Guide Optional Outputs>` by the new ``?`` syntax)


.. _compat_required_changes:

Required Changes
----------------

Providing your Cylc 7 workflow does not use syntax that was deprecated at Cylc 7,
you may be able to run it using Cylc 8 without any modifications while in
compatibility mode.

First, run ``cylc validate`` **with Cylc 7** on your ``suite.rc`` workflow
to check for deprecation warnings and fix those before validating with Cylc 8.
See :ref:`below <compat.eg.c7val>` for an example.

.. warning::

   ``cylc validate`` operates on the processed ``suite.rc``, which
   means it will not detect any deprecated syntax that is inside a
   currently-unused Jinja2/EmPy ``if...else`` branch.

Some workflows may require modifications to either upgrade to Cylc 8 or make
interoperable with Cylc 8 backward compatibility mode. Read on for more details.


Cylc commands in task scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check for any use of Cylc commands in task scripting. Some Cylc 7 commands
have been removed and some others now behave differently.
However, ``cylc message`` and ``cylc broadcast`` have *not* changed.
See the :ref:`full list of command line interface changes<MajorChangesCLI>`
and see :ref:`below <compat.eg.cylc-commands>` for an example.


Python 2 to 3
^^^^^^^^^^^^^

Whereas Cylc 7 runs using Python 2, Cylc 8 runs using Python 3. This affects:
- modules imported in Jinja2
- Jinja2 filters, tests and globals
- custom xtrigger functions

Note that task scripts are not affected - they can run using an independent
environment.

See :ref:`py23` for more information and examples of how to implement
interoperability.


Restarting a Cylc 7 workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cylc 8 cannot *restart* a Cylc 7 workflow mid-run. Instead, :ref:`install
<Installing-workflows>` the workflow to a new run directory and start it
from scratch at the right cycle point or task(s):

- ``cylc play --start-cycle-point=<cycle>`` (c.f. Cylc 7 *warm start*), or
- ``cylc play --start-task=<cycle/task>``   (Cylc 8 can start anywhere in the graph)

.. note::

   Any previous-cycle workflow data needed by the new run will need to be
   manually copied over from the original run directory.


Custom remote installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have used Rose 2019 you may be used to all files and directories inside
your :term:`source directory` being installed on remote install targets.
However, by default, Cylc 8 only installs
:ref:`certain files and directories <RemoteInit>` onto remote install targets.
See :ref:`below <compat.eg.custom_remote_install>` for an example of how to specify
custom files to be installed.


Other caveats
^^^^^^^^^^^^^

- Cylc 8 does not support
  :ref:`excluding/including tasks at start-up<MajorChangesExcludingTasksAtStartup>`.
  If your workflow used this old functionality, it may have been used in
  combination with the ``cylc insert`` command (which has been removed from
  Cylc 8) and ``cylc remove`` (which still exists but is much less needed).

- Cylc 8 does not support :ref:`specifying remote usernames <728.remote_owner>`
  using :cylc:conf:`flow.cylc[runtime][<namespace>][remote]owner`.


Examples
--------

.. _compat.eg.c7val:

Validating with Cylc 7
^^^^^^^^^^^^^^^^^^^^^^

Consider this configuration:

.. code-block:: cylc
   :caption: ``suite.rc``

   [scheduling]
       initial cycle point = 11000101T00
       [[dependencies]]
           [[[R1]]]
               graph = task

   [runtime]
       [[task]]
           pre-command scripting = echo "Hello World"

Running ``cylc validate`` at **Cylc 7** we see that the
workflow is valid, but we are warned that ``pre-command scripting``
was replaced by ``pre-script`` at 6.4.0:

.. code-block:: console
   :caption: Cylc 7 validation

   $ cylc validate .
   WARNING - deprecated items were automatically upgraded in 'suite definition':
   WARNING -  * (6.4.0) [runtime][task][pre-command scripting] -> [runtime][task][pre-script] - value unchanged
   Valid for cylc-7.8.7

.. note::

   **Cylc 7** has handled this deprecation for us, but at **Cylc 8** this
   workflow will fail validation.

   .. code-block:: console
      :caption: Cylc 8 validation

      $ cylc validate .
      IllegalItemError: [runtime][task]pre-command scripting

You must change the configuration yourself. In this case:

.. code-block:: diff

   -     pre-command scripting = echo "Hello World"
   +     pre-script = echo "Hello World"

Validation will now succeed.


.. _compat.eg.cylc-commands:

Cylc commands in task scripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You might have a task script that calls a Cylc command like so:

.. code-block:: cylc

   [runtime]
       [[foo]]
           script = cylc hold "$CYLC_SUITE_NAME"

The ``cylc hold`` command has changed in Cylc 8. It is now used for holding
tasks only; use ``cylc pause`` for entire workflows.
(Additionally, ``$CYLC_SUITE_NAME`` is deprecated in favour of
``$CYLC_WORKFLOW_ID``, though still supported.)

In order to make this interoperable, so that you can run it with both Cylc 7
and Cylc 8 backward compatibility mode, you could do something like this
in the bash script:

.. code-block:: cylc

   [runtime]
       [[foo]]
           script = """
               if [[ "${CYLC_VERSION:0:1}" == 7 ]]; then
                   cylc hold "$CYLC_SUITE_NAME"
               else
                   cylc pause "$CYLC_WORKFLOW_ID"
               fi
           """

Note this logic (and the ``$CYLC_VERSION`` environment variable) is executed
at runtime on the :term:`job host`.

Alternatively, you could use :ref:`Jinja` like so:

.. code-block:: cylc

   [runtime]
       [[foo]]
           {% if CYLC_VERSION is defined and CYLC_VERSION[0] == '8' %}
               script = cylc pause "$CYLC_WORKFLOW_ID"
           {% else %}
               script = cylc hold "$CYLC_SUITE_NAME"
           {% endif %}

Note this logic (and the ``CYLC_VERSION`` Jinja2 variable) is executed locally
prior to parsing the workflow configuration.


.. _compat.eg.custom_remote_install:

Custom remote installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to include certain files and directories in remote installation,
use :cylc:conf:`flow.cylc[scheduler]install`. To ensure your workflow is still
interoperable with Cylc 7, wrap it in a Jinja2 check like so:

.. code-block:: cylc

   {% if CYLC_VERSION is defined and CYLC_VERSION[0] == '8' %}
   [scheduler]
       install = my-dir/, my-file
   {% endif %}


Renaming to ``flow.cylc``
-------------------------

When your workflow runs successfully in backward compatibility mode, it is
ready for renaming ``suite.rc`` to ``flow.cylc``. Doing this will turn off
backward compatibility mode, and validation in Cylc 8 will show
deprecation warnings.

.. seealso::

   :ref:`configuration-changes`

.. important::

   More complex workflows (e.g. those with suicide triggers) may
   fail validation once backward compatibility is off - see
   :ref:`728.optional_outputs`


.. _host-to-platform-logic:

How Cylc 8 handles host-to-platform upgrades
--------------------------------------------

.. seealso::

   :ref:`Details of how platforms work.<MajorChangesPlatforms>`

   .. TODO reference to how to write platforms page

If you have a Cylc 7 workflow where tasks submit jobs to remote hosts,
Cylc 8 will attempt to find a platform which matches the task specification.

.. important::

   Cylc 8 needs platforms matching the Cylc 7 job configuration to be
   available in :cylc:conf:`global.cylc[platforms]`.

Example
^^^^^^^

.. note::

   In the following example, ``job runner`` in **Cylc 8** configurations
   and ``batch system`` in **Cylc 7** configurations refer to the same item.

If, for example you have a **Cylc 8** ``global.cylc`` with the following
platforms section:

.. code-block:: cylc

   [platforms]
       [[supercomputer_A]]
           hosts = localhost
           job runner = slurm
       [[supercomputer_B]]
           hosts = tigger, wol, eeyore
           job runner = pbs

And you have a workflow runtime configuration:

.. code-block:: cylc

   [runtime]
       [[task1]]
           [[[job]]]
               batch system = slurm
       [[task2]]
           [[[remote]]]
               hosts = eeyore
           [[[job]]]
               batch system = pbs

Then, ``task1`` will be assigned platform
``supercomputer_A`` because the specified host (implicitly ``localhost``)
is in the list of hosts for ``supercomputer_A`` **and** the batch system is the same.
Likewise, ``task2`` will run on ``supercomputer_B``.

.. important::

   For simplicity, and because the ``host`` key is a special case (it can
   match and host in ``[platform]hosts``) we only show these two config keys
   here. In reality, **Cylc 8 compares the whole of**
   ``[<task>][job]`` **and** ``[<task>][remote]``
   **sections and all items must match to select a platform.**
